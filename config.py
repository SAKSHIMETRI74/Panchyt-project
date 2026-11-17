import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "gp_default_dev_secret_key_9938472918471928")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "panchayat.db")
    
    # Protected Storage for evidence (Photos are NOT placed in static folder)
    PRIVATE_UPLOAD_FOLDER = os.path.join(BASE_DIR, "private_uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 5)) * 1024 * 1024 # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = 86400 # 24 hours
    
    # Panchayat Jurisdiction Limits (Coordinates for validation - default Karnataka bounding box)
    # Latitude: 11.5°N to 18.5°N, Longitude: 74.0°E to 78.5°E
    GEO_BOUNDS = {
        "min_lat": 11.0,
        "max_lat": 19.0,
        "min_lng": 73.5,
        "max_lng": 79.0
    }
    
    # Default Admin Configuration
    DEFAULT_ADMIN_PHONE = os.environ.get("DEFAULT_ADMIN_PHONE", "9876543210")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "PanchayatAdmin@2026")
    DEFAULT_ADMIN_NAME = os.environ.get("DEFAULT_ADMIN_NAME", "Panchayat Development Officer (PDO)")
    
    # Service Providers
    SMS_PROVIDER = os.environ.get("SMS_GATEWAY_PROVIDER", "mock")
    AI_PROVIDER = os.environ.get("AI_SERVICE_PROVIDER", "heuristic")
