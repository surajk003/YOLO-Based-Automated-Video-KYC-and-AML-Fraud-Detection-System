import base64
import hashlib
import hmac
import json
import os
import time
from typing import Dict, Tuple

from cryptography.fernet import Fernet


JWT_SECRET = os.getenv("SECUREFIN_JWT_SECRET", "securefin-dev-jwt-secret")
JWT_EXPIRY_SECONDS = int(os.getenv("SECUREFIN_JWT_EXPIRY_SECONDS", "1800"))
ENCRYPTION_SECRET = os.getenv("SECUREFIN_ENCRYPTION_SECRET", "securefin-dev-encryption-key")


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(message: bytes) -> str:
    digest = hmac.new(JWT_SECRET.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_jwt(user_id: str, role: str) -> Tuple[str, int]:
    expiry = int(time.time()) + JWT_EXPIRY_SECONDS
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user_id, "role": role, "exp": expiry}

    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    signature = _sign(signing_input)
    return f"{header_part}.{payload_part}.{signature}", expiry


def decode_jwt(token: str) -> Dict[str, object]:
    try:
        header_part, payload_part, signature = token.split(".")
    except ValueError as e:
        raise ValueError("Malformed JWT token") from e

    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    expected = _sign(signing_input)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_part))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired")

    return payload


def verify_password(password: str, stored_password: str) -> bool:
    return hmac.compare_digest(password, stored_password)


def get_fernet() -> Fernet:
    key_material = hashlib.sha256(ENCRYPTION_SECRET.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(key_material)
    return Fernet(key)


def encrypt_bytes(raw: bytes) -> bytes:
    return get_fernet().encrypt(raw)


def decrypt_bytes(ciphertext: bytes) -> bytes:
    return get_fernet().decrypt(ciphertext)
