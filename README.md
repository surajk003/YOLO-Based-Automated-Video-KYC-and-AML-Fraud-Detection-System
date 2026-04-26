# SecureFin Project

SecureFin is a KYC + AML verification demo project with a FastAPI backend and a browser-based frontend. It supports agent login, KYC document verification, guided liveness checks, AML risk scoring, audit logging, encrypted image storage, and evaluation graphs for AML and KYC runs.

## Features

- JWT-based login for agents and reviewers
- KYC verification flow with:
  - document OCR
  - face match against live capture
  - guided liveness challenge with text + spoken prompts
  - single-person check
- AML transaction risk scoring with Isolation Forest
- Audit trail and SQLite persistence
- Encrypted storage for uploaded KYC images
- Customer timeline and decision history
- AML evaluation graphs and confusion matrix
- KYC validation charts from stored runs

## Project Structure

```text
securefin_project/
├── backend/
│   ├── main.py
│   ├── aml.py
│   ├── kyc.py
│   ├── liveness.py
│   ├── ocr.py
│   ├── train_aml_model.py
│   ├── evaluate_aml_model.py
│   ├── evaluate_kyc_metrics.py
│   ├── aml_model.pkl
│   └── uploads/
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── database/
│   └── securefin.db
├── frontend_server.py
├── run_project.ps1
└── README.md
```

## Tech Stack

- Backend: FastAPI, Uvicorn
- Frontend: HTML, CSS, JavaScript
- AML Model: scikit-learn IsolationForest
- Face Verification: DeepFace
- OCR: Tesseract via `pytesseract`
- Computer Vision: OpenCV, YOLO
- Database: SQLite

## Setup

## 1. Create and activate virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you already have the existing project venv, you can reuse it.

## 2. Install dependencies

From the project root:

```powershell
pip install -r requirements.txt
```

Depending on your environment, some backend packages may also need to be installed from inside the backend setup you already used for the project.

## 3. Tesseract OCR

Install Tesseract OCR and make sure it is available on your system PATH.

Typical Windows install path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If needed, update the OCR configuration in the backend to point to your local Tesseract install.

## Running the Project

## Option 1. One-click launcher

From the inner project folder:

```powershell
cd "C:\Software Projects\Software Projects\securefin_project\securefin_project"
.\run_project.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_project.ps1
```

This opens two terminals:
- backend on `http://127.0.0.1:8000`
- frontend on `http://127.0.0.1:5500`

## Option 2. Run manually

Backend:

```powershell
cd "C:\Software Projects\Software Projects\securefin_project\securefin_project\backend"
& "C:\Software Projects\Software Projects\securefin_project\venv\Scripts\python.exe" -m uvicorn main:app --reload
```

Frontend:

```powershell
cd "C:\Software Projects\Software Projects\securefin_project\securefin_project"
& "C:\Software Projects\Software Projects\securefin_project\venv\Scripts\python.exe" frontend_server.py
```

## Default Login

- Username: `agent01`
- Password: `agent123`

Reviewer account:
- Username: `reviewer01`
- Password: `review123`

## Application Flow

## KYC

1. Log in as an agent.
2. Open the KYC screen.
3. Enter:
   - customer ID
   - full name
   - DOB
   - document type
4. Upload Aadhaar or PAN image.
5. Complete the guided liveness prompts:
   - look straight
   - turn left or right
   - blink
6. Submit for verification.

Backend checks:
- OCR extraction from document
- Name and DOB matching
- Face match between document and live frame
- Single-person detection
- Liveness challenge validation

## AML

1. Open the AML screen.
2. Enter:
   - customer ID
   - amount
   - old balance
   - new balance
   - transaction type
   - transaction date/time
3. Submit transaction.

AML output:
- risk score
- status: `ALLOW`, `REVIEW`, or `BLOCK`
- reason codes
- model version
- rule engine version

## API Endpoints

Authentication:
- `POST /auth/login`

KYC:
- `POST /kyc/verify`
- `GET /kyc/document/{request_id}`

AML:
- `POST /aml/check`

Audit / timeline:
- `GET /customer/{customer_id}/timeline`

## Stored Data

SQLite database:
- `database/securefin.db`

Main tables:
- `users`
- `kyc_requests`
- `aml_decisions`
- `audit_logs`

Uploaded KYC images are stored in encrypted form under:
- `backend/uploads/encrypted/`

## Evaluation Artifacts

## AML

Generated files in `backend/`:
- `aml_performance_graph.png`
- `aml_confusion_matrix.png`
- `aml_metrics.json`
- `aml_classification_report.txt`
- `evaluate_aml_model.py`

Observed AML metrics from the current saved model:
- Accuracy: `94.15%`
- Precision: `66.77%`
- Recall: `45.57%`
- F1 Score: `54.17%`
- ROC AUC: `0.899`
- Average Precision: `0.596`

Note: the saved `aml_model.pkl` shows a scikit-learn version mismatch warning in the current environment. Retraining in the active environment is recommended for cleaner reproducibility.

## KYC

Generated files in `backend/`:
- `kyc_status_distribution.png`
- `kyc_validation_parameters.png`
- `kyc_reason_code_frequency.png`
- `kyc_confidence_timeline.png`
- `kyc_metrics.json`
- `evaluate_kyc_metrics.py`

Important: current KYC charts are operational validation charts from stored project runs, not true model accuracy metrics, because the project does not yet include a labeled KYC benchmark dataset.

Current observed KYC validation rates from stored runs:
- DOB Match: `50.0%`
- Name Match: `40.91%`
- Face Match: `0.0%`
- Single Person: `90.91%`
- Turn Left: `36.36%`
- Turn Right: `75.0%`
- Blink: `94.74%`

## Known Limitations

- KYC face matching is currently the weakest component and is the main reason for verification failures.
- KYC does not yet have a labeled benchmark dataset for true accuracy measurement.
- OCR quality depends on image clarity and Tesseract installation.
- The AML model is unsupervised and tuned with rules layered on top.

## Recommended Next Improvements

- Calibrate and improve face matching threshold
- Add a labeled KYC evaluation dataset
- Improve OCR preprocessing for more document types
- Add dashboard embedding for evaluation charts
- Retrain AML model in the current scikit-learn version

## Troubleshooting

## `run_project.ps1` not found

Make sure you are inside the inner project folder:

```powershell
cd "C:\Software Projects\Software Projects\securefin_project\securefin_project"
```

## Port already in use

If frontend or backend ports are busy, stop the old terminals or processes and restart.

## PowerShell cannot run script

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

## Uvicorn cannot import `main`

Run backend from the `backend` folder, not from the outer folder.

## OCR not working

Check that Tesseract is installed and accessible from PATH.

## Author

Prepared for the SecureFin KYC/AML demo workflow.
