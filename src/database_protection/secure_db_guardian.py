"""
Secure Database Guardian - Complete database access control system
This wrapper intercepts ALL database operations and enforces strict permissions.
"""
import sqlite3
import threading
import time
import json
import os
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager


class SecureConnectionProxy:
    """Proxy that wraps sqlite3.Connection and controls all operations"""
    
    def __init__(self, real_connection: sqlite3.Connection, guardian: 'SecureDatabaseGuardian', 
                 app_id: str, ip_address: str):
        self._real_conn = real_connection
        self._guardian = guardian
        self._app_id = app_id
        self._ip_address = ip_address
        self._closed = False
        
    def execute(self, sql: str, parameters: tuple = ()):
        """Execute SQL through guardian permission system"""
        if self._closed:
            raise sqlite3.Error("Cannot operate on a closed database.")
        
        if not self._guardian.check_permission(self._app_id, self._ip_address, 'execute', sql):
            raise sqlite3.Error("Access denied by database guardian")
        
        return self._real_conn.execute(sql, parameters)
    
    def executemany(self, sql: str, parameters_list):
        """Execute many SQL statements through guardian"""
        if self._closed:
            raise sqlite3.Error("Cannot operate on a closed database.")
            
        if not self._guardian.check_permission(self._app_id, self._ip_address, 'executemany', sql):
            raise sqlite3.Error("Access denied by database guardian")
        
        return self._real_conn.executemany(sql, parameters_list)
    
    def cursor(self):
        """Create a secure cursor proxy"""
        if self._closed:
            raise sqlite3.Error("Cannot operate on a closed database.")
        return SecureCursorProxy(self._real_conn.cursor(), self._guardian, 
                               self._app_id, self._ip_address)
    
    def commit(self):
        """Commit transaction through guardian"""
        if self._closed:
            raise sqlite3.Error("Cannot operate on a closed database.")
            
        if not self._guardian.check_permission(self._app_id, self._ip_address, 'commit', ''):
            raise sqlite3.Error("Commit access denied by database guardian")
        
        return self._real_conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self._closed:
            raise sqlite3.Error("Cannot operate on a closed database.")
        return self._real_conn.rollback()
    
    def close(self):
        """Close connection"""
        if not self._closed:
            self._guardian.log_access(self._app_id, self._ip_address, 'close', '', 'success')
            self._real_conn.close()
            self._closed = True
    
    @property
    def row_factory(self):
        """Get row factory"""
        return self._real_conn.row_factory
    
    @row_factory.setter
    def row_factory(self, factory):
        """Set row factory"""
        self._real_conn.row_factory = factory
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SecureCursorProxy:
    """Proxy that wraps sqlite3.Cursor and controls all operations"""
    
    def __init__(self, real_cursor, guardian: 'SecureDatabaseGuardian', 
                 app_id: str, ip_address: str):
        self._real_cursor = real_cursor
        self._guardian = guardian
        self._app_id = app_id
        self._ip_address = ip_address
    
    def execute(self, sql: str, parameters: tuple = ()):
        """Execute SQL through guardian"""
        if not self._guardian.check_permission(self._app_id, self._ip_address, 'execute', sql):
            raise sqlite3.Error("Access denied by database guardian")
        
        return self._real_cursor.execute(sql, parameters)
    
    def executemany(self, sql: str, parameters_list):
        """Execute many SQL statements"""
        if not self._guardian.check_permission(self._app_id, self._ip_address, 'executemany', sql):
            raise sqlite3.Error("Access denied by database guardian")
        
        return self._real_cursor.executemany(sql, parameters_list)
    
    def fetchone(self):
        """Fetch one row"""
        return self._real_cursor.fetchone()
    
    def fetchmany(self, size=None):
        """Fetch many rows"""
        return self._real_cursor.fetchmany(size)
    
    def fetchall(self):
        """Fetch all rows"""
        return self._real_cursor.fetchall()
    
    def close(self):
        """Close cursor"""
        return self._real_cursor.close()
    
    @property
    def description(self):
        """Get column description"""
        return self._real_cursor.description
    
    @property
    def rowcount(self):
        """Get row count"""
        return self._real_cursor.rowcount


class SecureDatabaseGuardian:
    """Main guardian class that controls all database access"""
    
    def __init__(self, security_db_path: str = None):
        self.security_db_path = security_db_path or "security_guardian.db"
        self._lock = threading.RLock()
        self._permissions = {
            'default': {
                'read': True,
                'write': True,
                'create': False,
                'drop': False,
                'alter': False
            }
        }
        self._blocked_patterns = [
            "DROP TABLE",
            "DELETE FROM users WHERE",
            "UPDATE users SET",
            "ALTER TABLE",
            "-- INJECTION",
            "UNION SELECT",
            "OR '1'='1",
            "; DROP",
            "' OR",
            "\" OR"
        ]
        self._init_security_db()
    
    def _init_security_db(self):
        """Initialize security database for logging"""
        try:
            conn = sqlite3.connect(self.security_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    app_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    sql TEXT,
                    result TEXT NOT NULL,
                    blocked_reason TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize security database: {e}")
    
    def connect(self, database_path: str, app_id: str = "unknown", ip_address: str = "127.0.0.1"):
        """Create a secure connection to the database"""
        with self._lock:
            try:
                # Create the actual SQLite connection
                real_conn = sqlite3.connect(database_path)
                
                # Log the connection attempt
                self.log_access(app_id, ip_address, 'connect', database_path, 'success')
                
                # Return our secure proxy
                return SecureConnectionProxy(real_conn, self, app_id, ip_address)
            
            except Exception as e:
                self.log_access(app_id, ip_address, 'connect', database_path, 'failed', str(e))
                raise
    
    def check_permission(self, app_id: str, ip_address: str, operation: str, sql: str) -> bool:
        """Check if operation is permitted"""
        with self._lock:
            # Check for blocked patterns
            sql_upper = sql.upper()
            for pattern in self._blocked_patterns:
                if pattern in sql_upper:
                    self.log_access(app_id, ip_address, operation, sql, 'blocked', f'Pattern: {pattern}')
                    return False
            
            # Check operation type permissions
            if operation in ['execute', 'executemany']:
                # Check CREATE permissions
                if any(keyword in sql_upper for keyword in ['CREATE']):
                    if not self._permissions.get(app_id, self._permissions['default']).get('create', False):
                        self.log_access(app_id, ip_address, operation, sql, 'blocked', 'No create permission')
                        return False
                
                # Check DROP, DELETE, ALTER permissions  
                if any(keyword in sql_upper for keyword in ['DROP', 'DELETE', 'ALTER']):
                    if not self._permissions.get(app_id, self._permissions['default']).get('write', False):
                        self.log_access(app_id, ip_address, operation, sql, 'blocked', 'No write permission')
                        return False
                
                # Allow SELECT operations if read permission exists
                if sql_upper.strip().startswith('SELECT'):
                    if not self._permissions.get(app_id, self._permissions['default']).get('read', True):
                        self.log_access(app_id, ip_address, operation, sql, 'blocked', 'No read permission')
                        return False
            
            # Log successful permission check
            self.log_access(app_id, ip_address, operation, sql, 'allowed')
            return True
    
    def log_access(self, app_id: str, ip_address: str, operation: str, sql: str, 
                  result: str, blocked_reason: str = None):
        """Log database access attempts"""
        try:
            conn = sqlite3.connect(self.security_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs 
                (timestamp, app_id, ip_address, operation, sql, result, blocked_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.strftime('%Y-%m-%d %H:%M:%S'),
                app_id,
                ip_address,
                operation,
                sql[:500],  # Truncate long SQL
                result,
                blocked_reason
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not log access: {e}")
    
    def set_permissions(self, app_id: str, permissions: Dict[str, bool]):
        """Set permissions for an application"""
        with self._lock:
            self._permissions[app_id] = permissions
    
    def add_blocked_pattern(self, pattern: str):
        """Add a new blocked SQL pattern"""
        with self._lock:
            if pattern not in self._blocked_patterns:
                self._blocked_patterns.append(pattern)
    
    def get_access_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent access logs"""
        try:
            conn = sqlite3.connect(self.security_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM access_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return logs
        except Exception as e:
            print(f"Error getting logs: {e}")
            return []


# Global guardian instance
_guardian_instance = None


def initialize_secure_database(security_db_path: str = None) -> SecureDatabaseGuardian:
    """Initialize the secure database guardian"""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = SecureDatabaseGuardian(security_db_path)
    return _guardian_instance


def get_guardian() -> SecureDatabaseGuardian:
    """Get the current guardian instance"""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = SecureDatabaseGuardian()
    return _guardian_instance