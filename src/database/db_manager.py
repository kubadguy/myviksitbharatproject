import sqlite3
from typing import List, Tuple, Any
from config.settings import Settings
import os


class DatabaseManager:
    def __init__(self, db_path: str = None):
        """
        Initialize database manager
        """
        if db_path is None:
            db_path = Settings.REAL_DB_PATH
        
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _init_database(self):
        """Initialize database with default tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def execute_query(self, query: str, params: Tuple = None) -> List[Tuple]:
        """
        Execute a SELECT query and return results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return results
        finally:
            conn.close()

    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query
        Returns the number of affected rows
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a query with multiple parameter sets
        Returns the number of affected rows
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def create_user(self, username: str, email: str, password: str, balance: float = 0.0) -> int:
        """
        Create a new user
        Returns the user ID
        """
        query = '''
            INSERT INTO users (username, email, password, balance)
            VALUES (?, ?, ?, ?)
        '''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (username, email, password, balance))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Tuple:
        """Get user by ID"""
        query = 'SELECT * FROM users WHERE id = ?'
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None

    def get_user_by_username(self, username: str) -> Tuple:
        """Get user by username"""
        query = 'SELECT * FROM users WHERE username = ?'
        results = self.execute_query(query, (username,))
        return results[0] if results else None

    def get_all_users(self) -> List[Tuple]:
        """Get all users"""
        query = 'SELECT * FROM users'
        return self.execute_query(query)

    def update_user_balance(self, user_id: int, new_balance: float) -> bool:
        """Update user balance"""
        query = 'UPDATE users SET balance = ? WHERE id = ?'
        affected = self.execute_update(query, (new_balance, user_id))
        return affected > 0

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        query = 'DELETE FROM users WHERE id = ?'
        affected = self.execute_update(query, (user_id,))
        return affected > 0

    def create_transaction(self, user_id: int, amount: float, transaction_type: str) -> int:
        """
        Create a new transaction
        Returns the transaction ID
        """
        query = '''
            INSERT INTO transactions (user_id, amount, transaction_type)
            VALUES (?, ?, ?)
        '''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (user_id, amount, transaction_type))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_user_transactions(self, user_id: int) -> List[Tuple]:
        """Get all transactions for a user"""
        query = 'SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC'
        return self.execute_query(query, (user_id,))

    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def clear_all_data(self):
        """Clear all data from all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM transactions')
            cursor.execute('DELETE FROM users')
            conn.commit()
        finally:
            conn.close()

    def close(self):
        """Close database connection (for compatibility)"""
        pass
