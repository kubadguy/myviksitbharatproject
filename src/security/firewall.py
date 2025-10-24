import sqlite3
import datetime
from typing import Dict, List, Tuple
from faker import Faker
import hashlib


class DatabaseFirewall:
    """Main firewall class that intercepts and validates database access"""

    def __init__(self, real_db_path: str = "real_database.db",
        honeypot_db_path: str = "honeypot_database.db"):
        self.real_db_path = real_db_path
        self.honeypot_db_path = honeypot_db_path
        self.fake = Faker()
        self.access_log = []
        self.authorized_schedule = {} # Format: {app_id: [(start_time, end_time)]}
        # Initialize databases
        self._init_real_database()
        self._init_honeypot_database()

    def _init_real_database(self):
        """Initialize the real database with sample data"""
        conn = sqlite3.connect(self.real_db_path)
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
        # add some sample accounts
        users = [
            ('admin', 'admin@example.com', hashlib.sha256(b'admin').hexdigest(), 10000.0),
            ('alice', 'alice@example.com', hashlib.sha256(b'alice').hexdigest(), 5000.0)
        ]
        cursor.executemany('''
            INSERT INTO users (username, email, password, balance)
            VALUES (?, ?, ?, ?)
        ''', users)
        conn.commit()
        conn.close()

    def _init_honeypot_database(self):
        """Initialize honeypot with fake-ish data"""
        conn = sqlite3.connect(self.honeypot_db_path)
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
        # populate honeypot with some fake entries
        cursor.execute("DELETE FROM users")
        fake_rows = []
        for i in range(1, 6):
            uname = self.fake.user_name()
            fake_rows.append((i, uname, self.fake.email(), hashlib.md5(self.fake.password().encode()).hexdigest(), round(self.fake.random.uniform(100, 1000), 2)))
        cursor.executemany('''
            INSERT INTO users (id, username, email, password, balance)
            VALUES (?, ?, ?, ?, ?)
        ''', fake_rows)
        conn.commit()
        conn.close()

    def register_authorized_access(self, app_id: str, start: datetime.time, end: datetime.time):
        """Register allowed schedule for an app"""
        self.authorized_schedule.setdefault(app_id, []).append((start, end))

    def _is_access_authorized(self, app_id: str, current_time: datetime.datetime) -> bool:
        """Simple authorization check based on self.authorized_schedule"""
        if app_id not in self.authorized_schedule:
            # default allow nothing
            return False
        windows = self.authorized_schedule[app_id]
        now = current_time.time()
        for start, end in windows:
            if start <= now <= end:
                return True
        return False

    def _generate_fake_data(self):
        """Used to create honeytokens / decoy responses"""
        return {
            'username': self.fake.user_name(),
            'email': self.fake.email(),
            'note': self.fake.sentence()
        }

    def _populate_honeypot(self, operation: str, query: str):
        """Convenience wrapper to ensure honeypot has data"""
        conn = sqlite3.connect(self.honeypot_db_path)
        cursor = conn.cursor()
        # ensure there is at least some fake data
        cursor.execute("DELETE FROM users")
        fake_rows = []
        for i in range(1, 6):
            uname = self.fake.user_name()
            fake_rows.append((i, uname, self.fake.email(), hashlib.md5(self.fake.password().encode()).hexdigest(), round(self.fake.random.uniform(100, 1000), 2)))
        cursor.executemany('''
            INSERT INTO users (id, username, email, password, balance)
            VALUES (?, ?, ?, ?, ?)
        ''', fake_rows)
        conn.commit()
        conn.close()

    def _log_intrusion(self, app_id: str, ip_address: str, operation: str, query: str, timestamp: datetime.datetime):
        entry = {
            'timestamp': timestamp.isoformat(),
            'app_id': app_id,
            'ip_address': ip_address,
            'operation': operation,
            'query': query
        }
        self.access_log.append(entry)

    def _send_alert(self, log_entry: dict):
        # Placeholder: integrate with alerts/alert_manager
        print("ALERT:", log_entry)

    def execute_query(self, app_id: str, ip_address: str, operation: str,
                      query: str) -> Tuple[bool, List]:
        """
        Main method to execute database queries through the firewall
        Returns: (is_authorized, results)
        """
        current_time = datetime.datetime.now()

        # Check authorization
        is_authorized = self._is_access_authorized(app_id, current_time)

        if is_authorized:
            # Execute on real database
            conn = sqlite3.connect(self.real_db_path)
            cursor = conn.cursor()
            cursor.execute(query)

            if operation.upper() in ['INSERT', 'UPDATE', 'DELETE']:
                conn.commit()
                results = []
            else:
                results = cursor.fetchall()

            conn.close()
            return True, results

        else:
            # Redirect to honeypot
            self._log_intrusion(app_id, ip_address, operation, query, current_time)
            self._populate_honeypot(operation, query)

            # Execute on honeypot database
            conn = sqlite3.connect(self.honeypot_db_path)
            cursor = conn.cursor()
            cursor.execute(query)

            if operation.upper() in ['INSERT', 'UPDATE', 'DELETE']:
                conn.commit()
                results = []
            else:
                try:
                    results = cursor.fetchall()
                except Exception:
                    results = []
            conn.close()
            return False, results