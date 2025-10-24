"""
Database Proxy Server - Transparent Database Firewall
Applications connect to this proxy instead of the real database.
The proxy intercepts all queries and applies security checks transparently.

Usage:
    # Start the proxy
    python -m src.database_protection.proxy_server --db-type=postgresql --port=5433
    
    # Applications connect to localhost:5433 instead of real DB
    # They have no idea the firewall exists!
"""
import socket
import threading
import struct
import sys
import os
from typing import Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.firewall import DatabaseFirewall


class DatabaseProxyServer:
    """
    Transparent database proxy that intercepts connections
    """
    
    def __init__(self, 
                 listen_host: str = '0.0.0.0',
                 listen_port: int = 5433,
                 target_host: str = 'localhost',
                 target_port: int = 5432,
                 db_type: str = 'postgresql'):
        
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.db_type = db_type
        
        self.firewall = DatabaseFirewall()
        self.running = False
        
    def start(self):
        """Start the proxy server"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.listen_host, self.listen_port))
        self.server_socket.listen(5)
        
        print(f"🔥 Database Firewall Proxy Started")
        print(f"   Listening on: {self.listen_host}:{self.listen_port}")
        print(f"   Forwarding to: {self.target_host}:{self.target_port}")
        print(f"   Database Type: {self.db_type}")
        print(f"   All queries will be intercepted and checked!\n")
        
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"📥 New connection from {client_address}")
                
                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket: socket.socket, client_address: Tuple):
        """Handle a client connection"""
        target_socket = None
        
        try:
            # Connect to real database
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((self.target_host, self.target_port))
            print(f"✅ Connected to target database for {client_address}")
            
            # Create bidirectional relay
            # Client -> Server (intercept queries here)
            client_to_server = threading.Thread(
                target=self.relay_and_intercept,
                args=(client_socket, target_socket, client_address, True)
            )
            
            # Server -> Client (passthrough responses)
            server_to_client = threading.Thread(
                target=self.relay_and_intercept,
                args=(target_socket, client_socket, client_address, False)
            )
            
            client_to_server.daemon = True
            server_to_client.daemon = True
            
            client_to_server.start()
            server_to_client.start()
            
            # Wait for threads to finish
            client_to_server.join()
            server_to_client.join()
            
        except Exception as e:
            print(f"❌ Error handling client {client_address}: {e}")
        finally:
            if target_socket:
                target_socket.close()
            client_socket.close()
            print(f"🔌 Connection closed for {client_address}")
    
    def relay_and_intercept(self, source: socket.socket, destination: socket.socket, 
                           client_address: Tuple, intercept: bool):
        """
        Relay data between sockets, intercepting queries if needed
        
        Args:
            source: Source socket
            destination: Destination socket
            client_address: Client address for logging
            intercept: Whether to intercept and analyze (client->server direction)
        """
        try:
            while self.running:
                data = source.recv(4096)
                if not data:
                    break
                
                if intercept and self.db_type == 'postgresql':
                    # Try to extract and check PostgreSQL queries
                    query = self.extract_postgresql_query(data)
                    if query:
                        print(f"🔍 Intercepted query from {client_address}: {query[:100]}...")
                        
                        # Check with firewall
                        is_auth, results, reason = self.firewall.execute_query(
                            app_id=f"proxy_{client_address[0]}",
                            ip_address=client_address[0],
                            operation=self.detect_operation(query),
                            query=query
                        )
                        
                        if not is_auth:
                            print(f"🚫 BLOCKED query from {client_address}: {reason}")
                            # Send error response instead of forwarding
                            self.send_error_response(destination, reason)
                            continue
                        else:
                            print(f"✅ ALLOWED query from {client_address}")
                
                # Forward data to destination
                destination.sendall(data)
                
        except Exception as e:
            if self.running:
                print(f"Relay error for {client_address}: {e}")
    
    def extract_postgresql_query(self, data: bytes) -> Optional[str]:
        """
        Extract SQL query from PostgreSQL protocol packet
        Very simplified - in production you'd use a proper protocol parser
        """
        try:
            # PostgreSQL Simple Query (Q) or Extended Query (P)
            if len(data) < 5:
                return None
            
            message_type = chr(data[0])
            
            # Simple Query
            if message_type == 'Q':
                # Length is bytes 1-4, query starts at byte 5
                query = data[5:].split(b'\x00')[0].decode('utf-8', errors='ignore')
                return query.strip()
            
            # Parse (P) for prepared statements
            if message_type == 'P':
                # Skip name and find query
                parts = data[1:].split(b'\x00')
                if len(parts) >= 2:
                    query = parts[1].decode('utf-8', errors='ignore')
                    return query.strip()
            
        except Exception as e:
            pass
        
        return None
    
    def detect_operation(self, query: str) -> str:
        """Detect query operation type"""
        query_upper = query.upper().strip()
        for op in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']:
            if query_upper.startswith(op):
                return op
        return 'SELECT'
    
    def send_error_response(self, client_socket: socket.socket, error_message: str):
        """Send error response to client"""
        try:
            if self.db_type == 'postgresql':
                # PostgreSQL error response format (simplified)
                error_msg = f"ERROR: Security policy violation: {error_message}\x00"
                error_bytes = error_msg.encode('utf-8')
                
                # Error Response message (E)
                message = b'E' + struct.pack('!I', len(error_bytes) + 4) + error_bytes
                client_socket.sendall(message)
        except:
            pass
    
    def stop(self):
        """Stop the proxy server"""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()


class SQLiteProxyServer:
    """
    SQLite-specific proxy using file system interception
    Since SQLite is file-based, we intercept at the wrapper level
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.firewall = DatabaseFirewall()
        print(f"🔥 SQLite Firewall Active")
        print(f"   Database: {db_path}")
        print(f"   Use secure_db_wrapper for transparent protection\n")


def main():
    """CLI entry point for proxy server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Firewall Proxy Server')
    parser.add_argument('--db-type', default='postgresql', 
                       choices=['postgresql', 'mysql', 'sqlite'],
                       help='Database type')
    parser.add_argument('--listen-host', default='0.0.0.0', 
                       help='Host to listen on')
    parser.add_argument('--listen-port', type=int, default=5433,
                       help='Port to listen on')
    parser.add_argument('--target-host', default='localhost',
                       help='Target database host')
    parser.add_argument('--target-port', type=int, default=5432,
                       help='Target database port')
    
    args = parser.parse_args()
    
    if args.db_type == 'mysql' and args.target_port == 5432:
        args.target_port = 3306
    
    proxy = DatabaseProxyServer(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        target_host=args.target_host,
        target_port=args.target_port,
        db_type=args.db_type
    )
    
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down proxy server...")
        proxy.stop()


if __name__ == '__main__':
    main()
