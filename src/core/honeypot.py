from database.fake_data_generator import FakeDataGenerator
import sqlite3

class Honeypot:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.fake_gen = FakeDataGenerator()
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
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

    def populate_fake_data(self, num_records: int = 5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")

        fake_data = self.fake_gen.generate_users(num_records)
        cursor.executemany('''
            INSERT INTO users (id, username, email, password, balance)
            VALUES (?, ?, ?, ?, ?)
        ''', fake_data)

        conn.commit()
        conn.close()

    def execute_query(self, query: str):
        self.populate_fake_data()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
            else:
                conn.commit()
                results = []
            return results
        except Exception as e:
            return []
        finally:
            conn.close()
