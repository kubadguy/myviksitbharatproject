from typing import List, Dict, Any, Tuple, Optional
from .base_adapter import BaseDatabaseAdapter

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class MySQLAdapter(BaseDatabaseAdapter):
    """MySQL database adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        if not MYSQL_AVAILABLE:
            raise ImportError("mysql-connector-python is not installed. Install it with: pip install mysql-connector-python")
    
    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                host=self.connection_config.get('host', 'localhost'),
                port=self.connection_config.get('port', 3306),
                database=self.connection_config.get('database', 'mysql'),
                user=self.connection_config.get('user', 'root'),
                password=self.connection_config.get('password', ''),
            )
            return True
        except Exception as e:
            print(f"MySQL connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        if not self.connection:
            raise ConnectionError("Database not connected")
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return list(cursor.fetchall())
        finally:
            cursor.close()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
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
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        if not self.connection:
            raise ConnectionError("Database not connected")
        
        columns = ', '.join([f"`{col}` {dtype}" for col, dtype in schema.items()])
        query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
        
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
        return "mysql"
    
    def get_tables(self) -> List[str]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables
