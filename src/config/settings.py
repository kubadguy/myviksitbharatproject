import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    # Database settings
    REAL_DB_PATH = os.path.join(BASE_DIR, 'data', 'real_database.db')
    HONEYPOT_DB_PATH = os.path.join(BASE_DIR, 'data', 'honeypot_database.db')

    # Security settings
    MAX_FAILED_ATTEMPTS = 3
    ALERT_THRESHOLD = 5

    # Alert settings
    ENABLE_EMAIL_ALERTS = True
    ENABLE_SMS_ALERTS = False
    ADMIN_EMAIL = "admin@company.com"

    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    API_DEBUG = False
