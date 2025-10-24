from typing import List, Dict, Any, Tuple, Optional
from .base_adapter import BaseDatabaseAdapter

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class PostgreSQLAdapter(BaseDatabaseAdapter):
    """PostgreSQL database adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is not installed. Install it with: pip install psycopg2-binary")
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.connection_config.get('host', 'localhost'),
                port=self.connection_config.get('port', 5432),
                database=self.connection_config.get('database', 'postgres'),
                user=self.connection_config.get('user', 'postgres'),
                password=self.connection_config.get('password', ''),
                cursor_factory=RealDictCursor
            )
            self.connection.autocommit = False
            return True
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
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
            
            results = [dict(row) for row in cursor.fetchall()]
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
        except Exception as e:
            self.connection.rollback()
            raise e
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
            self.connection.rollback()
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
        return "postgresql"
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row['tablename'] for row in cursor.fetchall()]
        cursor.close()
        return tables
