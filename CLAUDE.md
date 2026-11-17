# CLAUDE.md - Gram Panchayat Portal Agent Context

You are the dedicated software engineer and administrator for the **Gram Panchayat Digital Grievance Portal** (ಗ್ರಾಮ ಪಂಚಾಯತ್ ಡಿಜಿಟಲ್ ಕುಂದುಕೊರತೆ ನಿವಾರಣಾ ಪೋರ್ಟಲ್).

## Project Overview
A production-ready bilingual (English & Kannada) civic grievance redressal portal built with Flask, SQLite, and Tailwind CSS for rural local government administration.

## Core System Architecture
- `app.py`: Main Flask controller, route handling, role-based authorization, and REST APIs.
- `database.py`: SQLite connection factory (`panchayat.db`), schema migrations, and initial data seeding.
- `models.py` / `database.py`: 5 relational tables (`users`, `phone_otps`, `complaints`, `complaint_audit_logs`, `complaint_appeals`).
- `otp_service.py`: Indian phone verification (`^[6-9]\d{9}$`), cryptographic 6-digit OTPs, 5-minute expiry, rate limiting, and SMS gateways.
- `ai_verifier.py`: Evidence photo verification, magic byte checks, Pillow integrity, and civic relevance heuristic.
- `translations.py`: Complete dictionary for English and authentic Kannada (`kn`).
- `templates/`: Jinja2 templates (`base.html`, `index.html`, `admin.html`).
- `static/js/app.js`: Client-side logic for OTP timer, GPS geolocation consent, AJAX form submissions, and modals.
- `private_uploads/`: Secure folder OUTSIDE public web root for complaint photos, served only via authenticated `/media/complaint/<id>/<photo>`.

## Development & Execution Commands
- **Activate Virtual Environment**:
  - CMD: `venv\Scripts\activate`
  - PowerShell: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\venv\Scripts\Activate.ps1`
- **Install Dependencies**: `pip install -r requirements.txt`
- **Initialize Database**: `python -c "import database; database.init_db()"`
- **Start Web Application**: `python app.py` (Runs on `http://127.0.0.1:5000`)
- **Run Unit Tests**: `python -m unittest discover -s tests`

## Key Business & Governance Rules
1. **Phone OTP Verification**: All new citizen registrations require mobile OTP validation. In dev mode, OTP is logged to console and returned in JSON response.
2. **Human-in-the-Loop AI**: AI analyzes photos and provides a confidence score, but NEVER auto-rejects complaints. Low-confidence photos are flagged for administrator inspection.
3. **Graduated False Complaint Policy**: Strikes 1 and 2 are warnings. Strike 3 restricts account. Citizens have 14 days to appeal via `/api/complaints/<id>/appeal`.
4. **Mandatory Audit Logging**: Every status change, severity revision, technician assignment, or appeal review MUST insert an entry into `complaint_audit_logs`.
5. **Private Storage**: Evidence photos must NEVER be placed in `static/uploads`. Always use `private_uploads/` with access verification.
