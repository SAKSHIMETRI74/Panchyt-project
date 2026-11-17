# Gram Panchayat Digital Grievance Portal (ಗ್ರಾಮ ಪಂಚಾಯತ್ ಡಿಜಿಟಲ್ ಪೋರ್ಟಲ್)

An enterprise-ready, bilingual (English + Kannada) civic complaint and grievance redressal system engineered for Indian Gram Panchayats. Built in compliance with the **10 November 2026 Project Audit & Review Standards**.

---

## Key Features & Audit Fixes Implemented

1. **Phone OTP Verification (Priority 1)**:
   - Validates 10-digit Indian mobile numbers (`^[6-9]\d{9}$`).
   - Dispatches 6-digit cryptographic OTPs with 5-minute expiry.
   - Throttles requests (max 3 OTPs per 15 min; max 3 verification attempts).
   - In development mode, the test OTP is printed to the terminal console and surfaced in the UI notification.
   - Ready integration for Indian SMS gateways (CDAC / NIC Mobile Seva, Fast2SMS).

2. **Fair Review & AI-Assisted Image Screening (Priority 2)**:
   - **AI Image Screening**: Evaluates photo relevance to civic infrastructure (water pipelines, road defects, drainage, streetlights) with an advisory confidence score.
   - **Human-in-the-Loop**: AI never auto-rejects complaints; anomalous or low-confidence photos are flagged for PDO review.
   - **Graduated False Complaint Policy**: Warnings on strikes 1 and 2; mandatory justification for strike 3 before account restriction.
   - **Citizen Appeals Desk**: Citizens can file formal appeals with supplementary evidence directly from their grievance tracking timeline.
   - **Comprehensive Audit Trail**: Every status change, severity revision, technician assignment, and appeal decision is recorded in `complaint_audit_logs`.

3. **Production Security Hardening (Priority 3)**:
   - **Protected Evidence Storage**: Uploaded complaint evidence is stored in `private_uploads/` outside the web root. Files are served strictly via authenticated access control (`@login_required`).
   - **GPS Boundary Validation**: Coordinates are validated server-side to fall within the state/Panchayat jurisdiction bounding box, accompanied by a clear citizen privacy consent notice.
   - **Session Security**: `HTTPOnly` session cookies with `SameSite=Lax` and configurable HTTPS enforcement.
   - **Password Security**: Strong cryptographic password hashing via Werkzeug.

4. **Bilingual Localization (Kannada & English)**:
   - Switch seamlessly between **English** and **ಕನ್ನಡ** with a single click.
   - Complete localized coverage across menus, badges, forms, SLAs, and error messages.

---

## Project Structure

```
gram-panchayat-portal/
├── app.py                     # Main Flask web application, routing, and APIs
├── config.py                  # Environment-driven configuration and security parameters
├── database.py                # SQLite schema creation, connections, and initial seeding
├── otp_service.py             # Phone OTP service, Indian regex, rate limiting, and SMS drivers
├── ai_verifier.py             # Image validation and civic AI relevance analyzer
├── translations.py            # Complete English and Kannada translation dictionary
├── requirements.txt           # Python package dependencies
├── .env.example               # Template for environment secrets
├── private_uploads/           # Protected storage for complaint photos (outside web root)
├── static/
│   ├── css/
│   │   └── styles.css         # Custom styling, active states, and print slip formatting
│   └── js/
│       └── app.js             # Client-side tabs, OTP timers, Geolocation, AJAX handlers
├── templates/
│   ├── base.html              # Base layout with bilingual navigation and modals
│   ├── index.html             # Citizen portal: File Grievance, Track Status, Transparency
│   └── admin.html             # Official console: Queue, AI alerts, Audit logs, Appeals desk
└── tests/
    └── test_portal.py         # Automated unit test suite
```

---

## Step-by-Step Setup in VS Code

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File -> Open Folder...**
3. Select this directory:
   ```
   C:\Users\Shrikant\.gemini\antigravity\scratch\gram-panchayat-portal
   ```

### Step 2: Open VS Code Integrated Terminal
Press `Ctrl + ~` (or go to **Terminal -> New Terminal** in the top menu).

### Step 3: Create and Activate a Python Virtual Environment
Run in PowerShell / Terminal:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(On Command Prompt, run `venv\Scripts\activate.bat`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: (Optional) Create `.env` from Example
```powershell
Copy-Item .env.example .env
```

### Step 6: Run the Application
```powershell
python app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## Pre-Configured Test Accounts

| Role | Mobile Number | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Panchayat Admin (PDO)** | `9876543210` | `PanchayatAdmin@2026` | Has full access to `/admin`, SLA updates, and Appeals Desk. |
| **Pre-Registered Citizen** | `9845012345` | `Citizen@123` | Has 3 pre-seeded sample grievances (`GP-2026-1001`, `1002`, `1003`). |

### Registering a New Citizen with OTP:
1. Click **"Register (OTP)"** on the top right.
2. Enter any 10-digit mobile number starting with 6, 7, 8, or 9 (e.g. `9811223344`).
3. Click **"Send OTP via SMS"**.
4. The test OTP will appear in the UI notification toast and in the VS Code terminal output (e.g. `482910`).
5. Enter the OTP, set your name and password, and submit!

---

## Running Automated Unit Tests
To verify all security validations, OTP rate limits, and schema operations:
```powershell
python -m unittest discover -s tests
```
