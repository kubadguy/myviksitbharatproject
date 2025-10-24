"""
Transparent Database Connection Wrapper
Intercepts all database operations and applies security checks
Applications use this exactly like sqlite3.connect() - no knowledge of protection

Supports: SQLite, PostgreSQL, MySQL
"""
import sqlite3
import inspect
import sys
import os
from typing import Any, Optional, Tuple, List, Dict

# Import firewall from core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.firewall import DatabaseFirewall as DatabaseSecurityFirewall

# Try to import PostgreSQL and MySQL drivers
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class SecureCursor:
    """Cursor wrapper that intercepts query execution"""
    
    def __init__(self, real_cursor, firewall: DatabaseSecurityFirewall, app_id: str, ip_address: str):
        self._cursor = real_cursor
        self._firewall = firewall
        self._app_id = app_id
        self._ip_address = ip_address
        self._last_results = None
    
    def execute(self, query: str, parameters: tuple = ()):
        """Intercept execute and apply security checks"""
        # Substitute parameters into query for security analysis
        full_query = query
        if parameters:
            # For security analysis, we need to see the full query
            full_query = query
            for param in parameters:
                if isinstance(param, str):
                    full_query = full_query.replace('?', f"'{param}'", 1)
                else:
                    full_query = full_query.replace('?', str(param), 1)
        
        # Determine operation type
        operation = query.strip().split()[0].upper()
        
        # Apply security check
        is_authorized, results, reason = self._firewall.execute_query(
            app_id=self._app_id,
            ip_address=self._ip_address,
            operation=operation,
            query=full_query
        )
        
        if is_authorized:
            # Execute real query
            self._cursor.execute(query, parameters)
            self._last_results = None
            return self
        else:
            # Query blocked - store honeypot results
            self._last_results = results
            # Raise exception to mimic blocked query
            raise sqlite3.OperationalError(f"Security violation: {reason}")
    
    def executemany(self, query: str, parameters):
        """Intercept executemany"""
        # For now, just execute first to check security
        if parameters:
            first_params = next(iter(parameters))
            self.execute(query, first_params)
            # If authorized, execute the rest
            return self._cursor.executemany(query, parameters)
        return self._cursor.executemany(query, parameters)
    
    def fetchone(self):
        """Fetch one result"""
        if self._last_results is not None:
            return self._last_results[0] if self._last_results else None
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all results"""
        if self._last_results is not None:
            return self._last_results
        return self._cursor.fetchall()
    
    def fetchmany(self, size=1):
        """Fetch many results"""
        if self._last_results is not None:
            return self._last_results[:size]
        return self._cursor.fetchmany(size)
    
    def __getattr__(self, name):
        """Proxy all other attributes to real cursor"""
        return getattr(self._cursor, name)


class SecureConnection:
    """Connection wrapper that creates secure cursors"""
    
    def __init__(self, real_connection, firewall: DatabaseSecurityFirewall, app_id: str, ip_address: str):
        self._connection = real_connection
        self._firewall = firewall
        self._app_id = app_id
        self._ip_address = ip_address
    
    def cursor(self):
        """Return a secure cursor"""
        real_cursor = self._connection.cursor()
        return SecureCursor(real_cursor, self._firewall, self._app_id, self._ip_address)
    
    def execute(self, query: str, parameters: tuple = ()):
        """Direct execute on connection"""
        cursor = self.cursor()
        return cursor.execute(query, parameters)
    
    def commit(self):
        """Commit transaction"""
        return self._connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        return self._connection.rollback()
    
    def close(self):
        """Close connection"""
        return self._connection.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
    
    def __getattr__(self, name):
        """Proxy all other attributes to real connection"""
        return getattr(self._connection, name)


class SecureDatabaseWrapper:
    """
    Transparent database wrapper that intercepts all database operations
    
    Usage from application (FastAPI, Django, etc.):
        # SQLite
        conn = secure_db.connect('db.sqlite3', app_id='my_app')
        
        # PostgreSQL
        conn = secure_db.connect_postgresql(host='localhost', database='mydb', 
                                           user='user', password='pass', app_id='my_app')
        
        # MySQL
        conn = secure_db.connect_mysql(host='localhost', database='mydb',
                                       user='user', password='pass', app_id='my_app')
        
    The application doesn't need to know about security - it's transparent!
    """
    
    def __init__(self, firewall: DatabaseSecurityFirewall):
        self.firewall = firewall
    
    def connect(self, database: str, app_id: str, ip_address: str = "127.0.0.1", **kwargs) -> SecureConnection:
        """
        Connect to SQLite database with transparent security
        
        Args:
            database: Database path
            app_id: Application identifier (must be registered in dashboard)
            ip_address: IP address of the connection
            **kwargs: Additional sqlite3.connect arguments
        
        Returns:
            SecureConnection that looks and acts like sqlite3.Connection
        """
        # Create real connection
        real_connection = sqlite3.connect(database, **kwargs)
        
        # Wrap it with security
        return SecureConnection(real_connection, self.firewall, app_id, ip_address)
    
    def connect_postgresql(self, host: str, database: str, user: str, password: str,
                          app_id: str, ip_address: str = "127.0.0.1", 
                          port: int = 5432, **kwargs) -> SecureConnection:
        """
        Connect to PostgreSQL database with transparent security
        
        Args:
            host: Database host
            database: Database name
            user: Username
            password: Password
            app_id: Application identifier
            ip_address: IP address of the connection
            port: Database port (default 5432)
            **kwargs: Additional psycopg2.connect arguments
        
        Returns:
            SecureConnection that intercepts all queries
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 not available. Install with: pip install psycopg2-binary")
        
        real_connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            **kwargs
        )
        
        return SecureConnection(real_connection, self.firewall, app_id, ip_address)
    
    def connect_mysql(self, host: str, database: str, user: str, password: str,
                     app_id: str, ip_address: str = "127.0.0.1",
                     port: int = 3306, **kwargs) -> SecureConnection:
        """
        Connect to MySQL database with transparent security
        
        Args:
            host: Database host
            database: Database name
            user: Username
            password: Password
            app_id: Application identifier
            ip_address: IP address of the connection
            port: Database port (default 3306)
            **kwargs: Additional mysql.connector.connect arguments
        
        Returns:
            SecureConnection that intercepts all queries
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python not available. Install with: pip install mysql-connector-python")
        
        real_connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            **kwargs
        )
        
        return SecureConnection(real_connection, self.firewall, app_id, ip_address)


# Global instance for easy import
_global_firewall = None

def initialize_secure_database(db_path: str = "security.db"):
    """Initialize the global secure database wrapper"""
    global _global_firewall
    _global_firewall = DatabaseSecurityFirewall()
    return SecureDatabaseWrapper(_global_firewall)

def get_secure_wrapper() -> SecureDatabaseWrapper:
    """Get the global secure database wrapper"""
    if _global_firewall is None:
        raise RuntimeError("Secure database not initialized. Call initialize_secure_database() first")
    return SecureDatabaseWrapper(_global_firewall)
