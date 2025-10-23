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
        self.authorized_schedule = {}  # Format: {app_id: [(start_time, end_time)]}

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

        # Insert sample real data
        cursor.execute("DELETE FROM users")
        cursor.executemany('''
            INSERT INTO users (username, email, password, balance) 
            VALUES (?, ?, ?, ?)
        ''', [
            ('admin', 'admin@company.com', 'hashed_password_1', 50000.00),
            ('john_doe', 'john@company.com', 'hashed_password_2', 25000.00),
            ('jane_smith', 'jane@company.com', 'hashed_password_3', 30000.00)
        ])

        conn.commit()
        conn.close()

    def _init_honeypot_database(self):
        """Initialize honeypot database with same schema"""
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

        conn.commit()
        conn.close()

    def register_authorized_access(self, app_id: str, time_windows: List[Tuple[int, int]]):
        """
        Register authorized time windows for an application
        time_windows: List of (start_hour, end_hour) tuples in 24-hour format
        """
        self.authorized_schedule[app_id] = time_windows

    def _is_access_authorized(self, app_id: str, current_time: datetime.datetime) -> bool:
        """Check if the application is authorized to access at current time"""
        if app_id not in self.authorized_schedule:
            return False

        current_hour = current_time.hour

        for start_hour, end_hour in self.authorized_schedule[app_id]:
            if start_hour <= current_hour < end_hour:
                return True

        return False

    def _generate_fake_data(self, num_records: int = 3) -> List[Tuple]:
        """Generate realistic fake data for the honeypot"""
        fake_data = []
        for i in range(1, num_records + 1):
            fake_data.append((
                i,
                self.fake.user_name(),
                self.fake.email(),
                hashlib.md5(self.fake.password().encode()).hexdigest(),
                round(self.fake.random.uniform(1000, 10000), 2)
            ))
        return fake_data

    def _populate_honeypot(self, operation: str, query: str):
        """Populate honeypot with fake data based on the operation"""
        conn = sqlite3.connect(self.honeypot_db_path)
        cursor = conn.cursor()

        # Clear and populate with fake data
        cursor.execute("DELETE FROM users")
        fake_data = self._generate_fake_data()

        cursor.executemany('''
            INSERT INTO users (id, username, email, password, balance) 
            VALUES (?, ?, ?, ?, ?)
        ''', fake_data)

        conn.commit()
        conn.close()

    def _log_intrusion(self, app_id: str, ip_address: str, operation: str,
                       query: str, timestamp: datetime.datetime):
        """Log unauthorized access attempt"""
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'app_id': app_id,
            'ip_address': ip_address,
            'operation': operation,
            'query': query,
            'action': 'REDIRECTED_TO_HONEYPOT'
        }

        self.access_log.append(log_entry)

        # In real implementation, this would send email/SMS
        self._send_alert(log_entry)

    @staticmethod
    def _send_alert(log_entry: Dict):
        """Send alert to administrator (simulated)"""
        print("\n" + "=" * 70)
        print("🚨 SECURITY ALERT - UNAUTHORIZED DATABASE ACCESS DETECTED 🚨")
        print("=" * 70)
        print(f"Timestamp:    {log_entry['timestamp']}")
        print(f"Application:  {log_entry['app_id']}")
        print(f"IP Address:   {log_entry['ip_address']}")
        print(f"Operation:    {log_entry['operation']}")
        print(f"Query:        {log_entry['query']}")
        print(f"Action Taken: {log_entry['action']}")
        print("=" * 70 + "\n")

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
            print(f"✅ Authorized access: {app_id} executed query on REAL database")
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
                results = cursor.fetchall()

            conn.close()
            print(f"❌ Unauthorized access: {app_id} redirected to HONEYPOT database")
            return False, results

    def get_access_logs(self) -> List[Dict]:
        """Retrieve all access logs"""
        return self.access_log


# Example usage demonstration
if __name__ == "__main__":
    print("Initializing Database Firewall System...\n")

    # Create firewall instance
    firewall = DatabaseFirewall()

    # Register authorized access windows
    # Format: app_id, [(start_hour, end_hour)]
    firewall.register_authorized_access('legitimate_app', [(9, 17)])  # 9 AM to 5 PM
    firewall.register_authorized_access('backup_service', [(2, 4)])  # 2 AM to 4 AM

    print("Authorized Access Windows:")
    print("- legitimate_app: 9:00 AM - 5:00 PM")
    print("- backup_service: 2:00 AM - 4:00 AM\n")

    # Simulate different access attempts
    print("\n--- SIMULATION 1: Authorized Access (within time window) ---")
    authorized, results = firewall.execute_query(
        app_id='legitimate_app',
        ip_address='192.168.1.100',
        operation='SELECT',
        query='SELECT * FROM users'
    )
    print(f"Results: {results}\n")

    print("\n--- SIMULATION 2: Unauthorized Access (outside time window) ---")
    unauthorized, results = firewall.execute_query(
        app_id='legitimate_app',  # Same app but outside time window
        ip_address='192.168.1.100',
        operation='SELECT',
        query='SELECT * FROM users WHERE username="admin"'
    )
    print(f"Results (from honeypot): {results}\n")

    print("\n--- SIMULATION 3: Unknown Application ---")
    malicious, results = firewall.execute_query(
        app_id='unknown_malicious_app',
        ip_address='203.0.113.42',  # Suspicious external IP
        operation='SELECT',
        query='SELECT password FROM users'
    )
    print(f"Results (from honeypot): {results}\n")

    print("\n--- SIMULATION 4: SQL Injection Attempt ---")
    injection, results = firewall.execute_query(
        app_id='hacker_tool',
        ip_address='198.51.100.23',
        operation='SELECT',
        query="SELECT * FROM users WHERE username='' OR '1'='1'"
    )
    print(f"Results (from honeypot): {results}\n")

    # Display all logged intrusions
    print("\n" + "=" * 70)
    print("INTRUSION LOG SUMMARY")
    print("=" * 70)
    logs = firewall.get_access_logs()
    print(f"Total unauthorized access attempts: {len(logs)}")
    for i, log in enumerate(logs, 1):
        print(f"\n[{i}] {log['timestamp']}")
        print(f"    App: {log['app_id']} | IP: {log['ip_address']}")
        print(f"    Query: {log['query']}")