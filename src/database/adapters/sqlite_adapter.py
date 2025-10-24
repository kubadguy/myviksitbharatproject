import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from .base_adapter import BaseDatabaseAdapter


class SQLiteAdapter(BaseDatabaseAdapter):
    """SQLite database adapter"""
    
    def connect(self) -> bool:
        """Establish connection to SQLite database"""
        try:
            db_path = self.connection_config.get('database', ':memory:')
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """Execute a SELECT query"""
        if not self.connection:
            raise ConnectionError("Database not connected")
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Convert rows to dictionaries
            columns = [column[0] for column in cursor.description] if cursor.description else []
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        finally:
            cursor.close()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query"""
        if not self.connection:
            raise ConnectionError("Database not connected")
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create a table with the given schema"""
        if not self.connection:
            raise ConnectionError("Database not connected")
        
        columns = ', '.join([f"{col} {dtype}" for col, dtype in schema.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Table creation error: {e}")
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test the database connection"""
        try:
            if not self.connection:
                if not self.connect():
                    return False, "Failed to establish connection"
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def get_database_type(self) -> str:
        """Get the type of database"""
        return "sqlite"
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """Get the schema of a table"""
        if not self.connection:
            return {}
        
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = {row[1]: row[2] for row in cursor.fetchall()}
        cursor.close()
        return schema
