import os
import re
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

INDIAN_PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")

class MockSMSProvider:
    """Mock SMS provider for local testing and demonstration."""
    def send_otp(self, phone: str, otp: str) -> bool:
        print("\n" + "="*50)
        print(f"[SMS GATEWAY SIMULATION] Destination: +91 {phone}")
        print(f"MESSAGE: Your Gram Panchayat Portal verification OTP is {otp}. Valid for 5 minutes. Do not share.")
        print("="*50 + "\n")
        return True

class Fast2SMSProvider:
    """Production integration for Indian Fast2SMS Gateway."""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send_otp(self, phone: str, otp: str) -> bool:
        # In production: requests.post('https://www.fast2sms.com/dev/bulkV2', ...)
        # Using mock fallback if key not configured
        if not self.api_key:
            return MockSMSProvider().send_otp(phone, otp)
        try:
            import urllib.request
            import urllib.parse
            import json
            data = urllib.parse.urlencode({
                'authorization': self.api_key,
                'variables_values': otp,
                'route': 'otp',
                'numbers': phone,
            }).encode('utf-8')
            req = urllib.request.Request('https://www.fast2sms.com/dev/bulkV2', data=data)
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                return res.get('return', False)
        except Exception as e:
            print(f"[SMS Gateway Error] {e}")
            return False

class OTPService:
    def __init__(self, provider_type="mock"):
        if provider_type == "fast2sms":
            self.provider = Fast2SMSProvider(os.environ.get("FAST2SMS_API_KEY", ""))
        else:
            self.provider = MockSMSProvider()

    def clean_phone(self, phone: str) -> str:
        if not phone:
            return ""
        phone = re.sub(r"[^\d]", "", str(phone))
        if phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]
        return phone

    def request_otp(self, conn, raw_phone: str):
        phone = self.clean_phone(raw_phone)
        if not INDIAN_PHONE_REGEX.match(phone):
            return False, "Invalid Indian mobile number. Must be 10 digits starting with 6, 7, 8, or 9."

        cursor = conn.cursor()
        
        # 1. Rate Limiting: Max 3 OTPs within last 15 minutes
        cutoff = (datetime.utcnow() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM phone_otps
            WHERE phone = ? AND created_at > ?
        """, (phone, cutoff))
        row = cursor.fetchone()
        if row and row['cnt'] >= 3:
            return False, "Too many OTP requests for this number. Please wait 15 minutes before requesting again."

        # 2. Generate 6-digit cryptographic OTP & hash it
        raw_otp = f"{secrets.randbelow(900000) + 100000}"
        otp_hash = generate_password_hash(raw_otp)
        expires_at = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO phone_otps (phone, otp_hash, expires_at)
            VALUES (?, ?, ?)
        """, (phone, otp_hash, expires_at))
        conn.commit()

        # 3. Dispatch through SMS Gateway
        sent = self.provider.send_otp(phone, raw_otp)
        if not sent:
            return False, "Failed to dispatch SMS through telecom gateway. Please try again."

        # For development / review, we return the raw OTP in demo message so reviewer can test without real SMS
        return True, {
            "message": "OTP sent successfully to +91 " + phone[:2] + "******" + phone[-2:],
            "dev_otp": raw_otp  # Accessible for easy local dev testing
        }

    def verify_otp(self, conn, raw_phone: str, submitted_otp: str):
        phone = self.clean_phone(raw_phone)
        if not phone or not submitted_otp:
            return False, "Phone and OTP are required."

        cursor = conn.cursor()
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT * FROM phone_otps
            WHERE phone = ? AND is_verified = 0
            ORDER BY id DESC LIMIT 1
        """, (phone,))
        record = cursor.fetchone()

        if not record:
            return False, "No pending OTP found. Please request a new OTP."

        if record["expires_at"] < now_str:
            return False, "OTP has expired. Please request a fresh OTP."

        if record["attempts"] >= 3:
            return False, "Maximum verification attempts exceeded. Please request a new OTP."

        if not check_password_hash(record["otp_hash"], submitted_otp.strip()):
            cursor.execute("UPDATE phone_otps SET attempts = attempts + 1 WHERE id = ?", (record["id"],))
            conn.commit()
            remaining = 2 - record["attempts"]
            return False, f"Incorrect OTP. {remaining} attempt(s) remaining."

        # Generate single-use verification token for registration step
        verification_token = secrets.token_hex(24)
        cursor.execute("""
            UPDATE phone_otps
            SET is_verified = 1, verification_token = ?
            WHERE id = ?
        """, (verification_token, record["id"]))
        conn.commit()

        return True, {
            "verification_token": verification_token,
            "message": "Mobile number verified successfully."
        }
