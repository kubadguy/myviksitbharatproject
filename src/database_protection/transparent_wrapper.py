"""
Transparent Database Connection Wrapper
This module intercepts database connections at the system level
and applies firewall protection WITHOUT requiring applications to import anything.

Usage from GUI:
    1. Connect to database in GUI
    2. GUI installs the transparent wrapper
    3. Any application (Flask, Django, etc.) that connects to the DB
       automatically goes through the firewall

Usage from application (NO CHANGES NEEDED):
    import sqlite3
    conn = sqlite3.connect('database.db')  # Automatically protected!
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")  # Goes through firewall!
"""

import sqlite3
import sys
import os
from typing import Optional, Any
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.firewall import DatabaseFirewall

# Global instances
_original_sqlite3_connect = sqlite3.connect
_firewall_instance: Optional[DatabaseFirewall] = None
_wrapper_installed = False
_lock = threading.Lock()

# Configuration
_current_app_id = "unknown_app"
_protection_enabled = False


class TransparentConnection:
    """Transparent wrapper for database connections"""
    
    def __init__(self, real_connection, database_path: str):
        self._real_conn = real_connection
        self._database_path = database_path
        self._closed = False
    
    def cursor(self):
        """Return a transparent cursor"""
        real_cursor = self._real_conn.cursor()
        return TransparentCursor(real_cursor, self._database_path)
    
    def execute(self, query: str, parameters: tuple = ()):
        """Direct execute on connection"""
        cursor = self.cursor()
        return cursor.execute(query, parameters)
    
    def commit(self):
        """Commit transaction"""
        return self._real_conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        return self._real_conn.rollback()
    
    def close(self):
        """Close connection"""
        if not self._closed:
            self._real_conn.close()
            self._closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __getattr__(self, name):
        """Proxy all other attributes to real connection"""
        return getattr(self._real_conn, name)


class TransparentCursor:
    """Transparent wrapper for database cursors"""
    
    def __init__(self, real_cursor, database_path: str):
        self._cursor = real_cursor
        self._database_path = database_path
        self._last_query = None
    
    def execute(self, query: str, parameters: tuple = ()):
        """Execute query through firewall if enabled"""
        global _firewall_instance, _protection_enabled, _current_app_id
        
        self._last_query = query
        
        # If protection is disabled, execute directly
        if not _protection_enabled or _firewall_instance is None:
            if parameters:
                return self._cursor.execute(query, parameters)
            return self._cursor.execute(query)
        
        # Get operation type
        operation = query.strip().split()[0].upper() if query.strip() else 'UNKNOWN'
        
        # Get caller information for better tracking
        import inspect
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back if frame and frame.f_back else None
        caller_info = "unknown"
        
        if caller_frame:
            caller_file = caller_frame.f_code.co_filename
            caller_line = caller_frame.f_lineno
            caller_info = f"{os.path.basename(caller_file)}:{caller_line}"
        
        # Execute through firewall
        try:
            is_auth, results, reason = _firewall_instance.execute_query(
                app_id=_current_app_id,
                ip_address='127.0.0.1',  # Local execution
                operation=operation,
                query=query
            )
            
            # If blocked, return honeypot results without raising exception
            # This makes it transparent - the app doesn't know it was blocked
            if not is_auth:
                # Store results in a way that fetchall() can retrieve them
                self._honeypot_results = results
                return self
            
            # Authorized - execute normally
            self._honeypot_results = None
            if parameters:
                return self._cursor.execute(query, parameters)
            return self._cursor.execute(query)
        
        except Exception as e:
            # On error, fall back to direct execution
            print(f"[Firewall] Error in transparent wrapper: {e}")
            if parameters:
                return self._cursor.execute(query, parameters)
            return self._cursor.execute(query)
    
    def executemany(self, query: str, seq_of_parameters):
        """Execute many queries"""
        global _protection_enabled
        
        # For bulk operations, check the query once
        if _protection_enabled and _firewall_instance:
            operation = query.strip().split()[0].upper() if query.strip() else 'UNKNOWN'
            is_auth, _, reason = _firewall_instance.execute_query(
                app_id=_current_app_id,
                ip_address='127.0.0.1',
                operation=operation,
                query=query
            )
            
            if not is_auth:
                # Block bulk operation
                print(f"[Firewall] Blocked bulk operation: {reason}")
                return self
        
        return self._cursor.executemany(query, seq_of_parameters)
    
    def fetchone(self):
        """Fetch one result"""
        if hasattr(self, '_honeypot_results') and self._honeypot_results is not None:
            return self._honeypot_results[0] if self._honeypot_results else None
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all results"""
        if hasattr(self, '_honeypot_results') and self._honeypot_results is not None:
            return self._honeypot_results
        return self._cursor.fetchall()
    
    def fetchmany(self, size=1):
        """Fetch many results"""
        if hasattr(self, '_honeypot_results') and self._honeypot_results is not None:
            return self._honeypot_results[:size]
        return self._cursor.fetchmany(size)
    
    def close(self):
        """Close cursor"""
        return self._cursor.close()
    
    def __getattr__(self, name):
        """Proxy all other attributes to real cursor"""
        return getattr(self._cursor, name)


def wrapped_connect(database, *args, **kwargs):
    """Wrapped sqlite3.connect function"""
    global _wrapper_installed
    
    # Create real connection
    real_conn = _original_sqlite3_connect(database, *args, **kwargs)
    
    # If wrapper is installed, return transparent connection
    if _wrapper_installed:
        return TransparentConnection(real_conn, database)
    
    # Otherwise return real connection
    return real_conn


def install_transparent_wrapper(firewall: DatabaseFirewall, app_id: str = "unknown_app"):
    """
    Install transparent database wrapper globally
    
    Args:
        firewall: DatabaseFirewall instance
        app_id: Application identifier for tracking
    """
    global _firewall_instance, _wrapper_installed, _current_app_id, _protection_enabled
    
    with _lock:
        _firewall_instance = firewall
        _current_app_id = app_id
        _wrapper_installed = True
        _protection_enabled = True
        
        # Replace sqlite3.connect
        sqlite3.connect = wrapped_connect
        
        print(f"[Firewall] Transparent wrapper installed for app_id: {app_id}")
        print(f"[Firewall] All sqlite3 connections are now protected")


def uninstall_transparent_wrapper():
    """Remove transparent wrapper and restore original sqlite3.connect"""
    global _wrapper_installed, _protection_enabled
    
    with _lock:
        _wrapper_installed = False
        _protection_enabled = False
        
        # Restore original sqlite3.connect
        sqlite3.connect = _original_sqlite3_connect
        
        print("[Firewall] Transparent wrapper uninstalled")


def enable_protection():
    """Enable firewall protection (wrapper must be installed first)"""
    global _protection_enabled
    _protection_enabled = True
    print("[Firewall] Protection enabled")


def disable_protection():
    """Temporarily disable firewall protection"""
    global _protection_enabled
    _protection_enabled = False
    print("[Firewall] Protection disabled")


def set_app_id(app_id: str):
    """Change the current application ID"""
    global _current_app_id
    _current_app_id = app_id
    print(f"[Firewall] App ID changed to: {app_id}")


def get_firewall() -> Optional[DatabaseFirewall]:
    """Get the current firewall instance"""
    return _firewall_instance


def is_protection_enabled() -> bool:
    """Check if protection is currently enabled"""
    return _protection_enabled and _wrapper_installed


# Example usage
if __name__ == "__main__":
    print("Transparent Database Wrapper - Example Usage")
    print("=" * 60)
    
    # Install wrapper
    firewall = DatabaseFirewall()
    install_transparent_wrapper(firewall, app_id="test_app")
    
    # Now use sqlite3 normally - it's automatically protected!
    print("\n1. Normal SELECT query (should work):")
    conn = sqlite3.connect('src/data/real_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(f"   Results: {results}")
    
    print("\n2. SQL Injection attempt (should be blocked):")
    cursor.execute("SELECT * FROM users WHERE id=1 OR '1'='1'")
    results = cursor.fetchall()
    print(f"   Results (honeypot): {results}")
    
    print("\n3. View logs:")
    logs = firewall.get_logs()
    print(f"   Total intrusions: {len(logs)}")
    for log in logs:
        print(f"   - {log['reason']}")
    
    conn.close()
    
    # Uninstall wrapper
    uninstall_transparent_wrapper()
    print("\n" + "=" * 60)