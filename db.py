import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / 'database'
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / 'securefin.db'


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        '''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS kyc_requests (
            request_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            submitted_by TEXT NOT NULL,
            status TEXT NOT NULL,
            reason_codes TEXT NOT NULL,
            confidence REAL NOT NULL,
            model_version TEXT NOT NULL,
            encrypted_document_path TEXT,
            encrypted_live_path TEXT,
            encrypted_live2_path TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS aml_decisions (
            decision_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            risk_score REAL NOT NULL,
            reason_codes TEXT NOT NULL,
            model_version TEXT NOT NULL,
            rule_engine_version TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            target_id TEXT NOT NULL,
            result TEXT NOT NULL,
            ip_address TEXT,
            trace_id TEXT,
            details TEXT,
            timestamp TEXT NOT NULL
        );
        '''
    )
    cur.execute(
        'INSERT OR IGNORE INTO users(user_id, username, password, role, created_at) VALUES (?, ?, ?, ?, datetime("now"))',
        ('U_AGENT01', 'agent01', 'agent123', 'agent'),
    )
    cur.execute(
        'INSERT OR IGNORE INTO users(user_id, username, password, role, created_at) VALUES (?, ?, ?, ?, datetime("now"))',
        ('U_REVIEWER01', 'reviewer01', 'review123', 'reviewer'),
    )
    conn.commit()
    conn.close()


def fetch_user(username: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_kyc_request(record: Dict[str, Any]) -> None:
    conn = get_connection()
    conn.execute(
        '''
        INSERT INTO kyc_requests(
            request_id, customer_id, submitted_by, status, reason_codes, confidence,
            model_version, encrypted_document_path, encrypted_live_path, encrypted_live2_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            record['request_id'], record['customer_id'], record['submitted_by'], record['status'],
            json.dumps(record['reason_codes']), record['confidence'], record['model_version'],
            record.get('encrypted_document_path'), record.get('encrypted_live_path'),
            record.get('encrypted_live2_path'), record['created_at']
        ),
    )
    conn.commit()
    conn.close()


def insert_aml_decision(record: Dict[str, Any]) -> None:
    conn = get_connection()
    conn.execute(
        '''
        INSERT INTO aml_decisions(
            decision_id, customer_id, amount, status, risk_score, reason_codes,
            model_version, rule_engine_version, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            record['decision_id'], record['customer_id'], record['amount'], record['status'],
            record['risk_score'], json.dumps(record['reason_codes']), record['model_version'],
            record['rule_engine_version'], record['created_at']
        ),
    )
    conn.commit()
    conn.close()


def insert_audit_log(record: Dict[str, Any]) -> None:
    conn = get_connection()
    conn.execute(
        '''
        INSERT INTO audit_logs(event_type, actor, action, target_id, result, ip_address, trace_id, details, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            record['event_type'], record['actor'], record['action'], record['target_id'],
            record['result'], record.get('ip_address'), record.get('trace_id'),
            json.dumps(record.get('details', {})), record['timestamp']
        ),
    )
    conn.commit()
    conn.close()


def fetch_customer_timeline(customer_id: str) -> Dict[str, List[Dict[str, Any]]]:
    conn = get_connection()
    kyc_rows = conn.execute('SELECT * FROM kyc_requests WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,)).fetchall()
    aml_rows = conn.execute('SELECT * FROM aml_decisions WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,)).fetchall()
    audit_rows = conn.execute(
        'SELECT * FROM audit_logs WHERE target_id = ? OR target_id IN (SELECT decision_id FROM aml_decisions WHERE customer_id = ?) ORDER BY timestamp DESC',
        (customer_id, customer_id),
    ).fetchall()
    conn.close()

    def convert(rows, json_fields):
        output = []
        for row in rows:
            item = dict(row)
            for field in json_fields:
                if item.get(field):
                    item[field] = json.loads(item[field])
            output.append(item)
        return output

    return {
        'kyc_requests': convert(kyc_rows, ['reason_codes']),
        'aml_decisions': convert(aml_rows, ['reason_codes']),
        'audit_logs': convert(audit_rows, ['details']),
    }
