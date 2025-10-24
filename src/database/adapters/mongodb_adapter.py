from typing import List, Dict, Any, Tuple, Optional
from .base_adapter import BaseDatabaseAdapter

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class MongoDBAdapter(BaseDatabaseAdapter):
    """MongoDB database adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        if not PYMONGO_AVAILABLE:
            raise ImportError("pymongo is not installed. Install it with: pip install pymongo")
        self.db = None
    
    def connect(self) -> bool:
        try:
            host = self.connection_config.get('host', 'localhost')
            port = self.connection_config.get('port', 27017)
            database = self.connection_config.get('database', 'test')
            username = self.connection_config.get('user')
            password = self.connection_config.get('password')
            
            if username and password:
                self.connection = MongoClient(
                    f"mongodb://{username}:{password}@{host}:{port}/{database}"
                )
            else:
                self.connection = MongoClient(host, port)
            
            self.db = self.connection[database]
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.db = None
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """
        For MongoDB, query should be a collection name, params should be a filter dict
        """
        if not self.db:
            raise ConnectionError("Database not connected")
        
        collection_name = query
        filter_dict = params[0] if params else {}
        
        collection = self.db[collection_name]
        results = list(collection.find(filter_dict))
        
        # Convert ObjectId to string for JSON compatibility
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return results
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        For MongoDB, query is collection name, params: (filter_dict, update_dict, operation)
        operation can be 'update', 'insert', 'delete'
        """
        if not self.db:
            raise ConnectionError("Database not connected")
        
        collection_name = query
        collection = self.db[collection_name]
        
        if not params or len(params) < 3:
            raise ValueError("MongoDB update requires (filter, update_data, operation)")
        
        filter_dict, update_data, operation = params[0], params[1], params[2]
        
        if operation == 'insert':
            result = collection.insert_one(update_data)
            return 1 if result.inserted_id else 0
        elif operation == 'update':
            result = collection.update_many(filter_dict, {'$set': update_data})
            return result.modified_count
        elif operation == 'delete':
            result = collection.delete_many(filter_dict)
            return result.deleted_count
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """MongoDB collections are created automatically, but we can create indexes"""
        if not self.db:
            raise ConnectionError("Database not connected")
        
        try:
            # Collection is created implicitly
            # We can create an index on common fields
            collection = self.db[table_name]
            if 'id' in schema:
                collection.create_index('id', unique=True)
            return True
        except Exception as e:
            print(f"Collection creation error: {e}")
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        try:
            if not self.connection:
                if not self.connect():
                    return False, "Failed to establish connection"
            
            # Ping the database
            self.connection.admin.command('ping')
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def get_database_type(self) -> str:
        return "mongodb"
    
    def get_tables(self) -> List[str]:
        """Get list of collections in MongoDB"""
        if not self.db:
            return []
        return self.db.list_collection_names()
