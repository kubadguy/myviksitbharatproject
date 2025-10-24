from core.access_control import AccessControl
from core.honeypot import Honeypot
from core.logger import SecurityLogger
from alerts.alert_manager import AlertManager
from security.injection_detector import InjectionDetector
from config.database_config import AUTHORIZED_APPS
from config.settings import Settings
import sqlite3

class DatabaseFirewall:
    def __init__(self):
        self.access_control = AccessControl(AUTHORIZED_APPS)
        self.honeypot = Honeypot(Settings.HONEYPOT_DB_PATH)
        self.logger = SecurityLogger()
        self.alert_manager = AlertManager()
        self.injection_detector = InjectionDetector()
        self._init_real_database()

    def _init_real_database(self):
        conn = sqlite3.connect(Settings.REAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                email TEXT,
                password TEXT,
                balance REAL
            )
        ''')
        cursor.execute("DELETE FROM users")
        cursor.executemany('''
            INSERT INTO users (username, email, password, balance)
            VALUES (?, ?, ?, ?)
        ''', [
            ('admin', 'admin@company.com', 'real_hash_1', 50000.00),
            ('john_doe', 'john@company.com', 'real_hash_2', 25000.00),
        ])
        conn.commit()
        conn.close()

    def execute_query(self, app_id: str, ip_address: str,
                     operation: str, query: str, simulate_time=None):
        import time
        start_time = time.time()
        
        # Check for injection
        is_injection, reason = self.injection_detector.detect_sql_injection(query)

        # Check authorization
        is_auth, auth_reason = self.access_control.is_authorized(
            app_id, ip_address, operation, simulate_time
        )

        if is_auth and not is_injection:
            # Execute on real database
            conn = sqlite3.connect(Settings.REAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query)
            if operation.upper() in ['INSERT', 'UPDATE', 'DELETE']:
                conn.commit()
                results = []
            else:
                results = cursor.fetchall()
            conn.close()
            
            # Log successful query
            execution_time = (time.time() - start_time) * 1000  # milliseconds
            self.logger.log_query(app_id, ip_address, operation, query, 
                                True, "Access granted", execution_time)
            return True, results, "Access granted"

        else:
            # Redirect to honeypot
            final_reason = reason if is_injection else auth_reason
            log_entry = self.logger.log_intrusion(
                app_id, ip_address, operation, query, final_reason
            )
            self.alert_manager.send_alert(log_entry)
            results = self.honeypot.execute_query(query)
            
            # Log blocked query
            execution_time = (time.time() - start_time) * 1000
            self.logger.log_query(app_id, ip_address, operation, query,
                                False, final_reason, execution_time)
            return False, results, final_reason

    def get_logs(self):
        return self.logger.get_logs()