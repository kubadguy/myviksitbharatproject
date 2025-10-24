"""
Flask adapter for integrating database security system
"""

from flask import request, g, jsonify
from functools import wraps
from typing import Callable, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.firewall import DatabaseFirewall


class FlaskSecurityAdapter:
    """
    Flask adapter for database security system
    
    Usage:
        from flask import Flask
        from framework_adapters import FlaskSecurityAdapter
        
        app = Flask(__name__)
        security = FlaskSecurityAdapter(app)
        
        @app.route('/api/users')
        @security.protect(app_id='my_app', operation='SELECT')
        def get_users():
            # Your query here
            pass
    """
    
    def __init__(self, app=None, firewall: Optional[DatabaseFirewall] = None):
        """
        Initialize Flask security adapter
        
        Args:
            app: Flask application instance (optional)
            firewall: Custom DatabaseFirewall instance (optional)
        """
        self.firewall = firewall or DatabaseFirewall()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the adapter with a Flask application
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Register before_request handler
        @app.before_request
        def before_request():
            g.db_security = self
    
    def protect(self, app_id: str, operation: str):
        """
        Decorator to protect database queries
        
        Args:
            app_id: Application identifier
            operation: SQL operation (SELECT, INSERT, UPDATE, DELETE)
        
        Usage:
            @security.protect(app_id='my_app', operation='SELECT')
            def my_route():
                query = "SELECT * FROM users"
                return security.execute(query)
        """
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Store context for use in execute method
                g.security_app_id = app_id
                g.security_operation = operation
                g.security_ip = request.remote_addr
                
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    def execute(self, query: str, simulate_time=None):
        """
        Execute a query through the security system
        
        Args:
            query: SQL query to execute
            simulate_time: Optional datetime for testing
        
        Returns:
            Tuple of (is_authorized, results, reason)
        """
        app_id = g.get('security_app_id', 'unknown')
        operation = g.get('security_operation', 'SELECT')
        ip_address = g.get('security_ip', request.remote_addr)
        
        return self.firewall.execute_query(
            app_id=app_id,
            ip_address=ip_address,
            operation=operation,
            query=query,
            simulate_time=simulate_time
        )
    
    def check_and_execute(self, app_id: str, operation: str, query: str):
        """
        Convenience method to check and execute a query in one call
        
        Args:
            app_id: Application identifier
            operation: SQL operation
            query: SQL query
        
        Returns:
            Flask Response object
        """
        ip_address = request.remote_addr
        
        is_auth, results, reason = self.firewall.execute_query(
            app_id=app_id,
            ip_address=ip_address,
            operation=operation,
            query=query
        )
        
        return jsonify({
            'authorized': is_auth,
            'results': results,
            'reason': reason
        }), 200 if is_auth else 403
    
    def get_logs(self, limit: Optional[int] = None):
        """Get security logs"""
        return self.firewall.get_logs()
    
    def create_routes(self, app, prefix='/api/security'):
        """
        Create security monitoring routes
        
        Args:
            app: Flask application
            prefix: URL prefix for routes
        """
        @app.route(f'{prefix}/logs', methods=['GET'])
        def get_security_logs():
            logs = self.get_logs()
            return jsonify({'logs': logs}), 200
        
        @app.route(f'{prefix}/stats', methods=['GET'])
        def get_security_stats():
            logs = self.get_logs()
            stats = {
                'total_queries': len(logs),
                'blocked_queries': sum(1 for log in logs if log['action'] == 'REDIRECTED_TO_HONEYPOT'),
                'unique_ips': len(set(log['ip_address'] for log in logs))
            }
            return jsonify(stats), 200
        
        @app.route(f'{prefix}/query', methods=['POST'])
        def execute_protected_query():
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({'error': 'Missing query parameter'}), 400
            
            return self.check_and_execute(
                app_id=data.get('app_id', 'unknown'),
                operation=data.get('operation', 'SELECT'),
                query=data['query']
            )


# Example Flask app integration
def create_protected_app():
    """Example of creating a Flask app with security protection"""
    from flask import Flask
    
    app = Flask(__name__)
    security = FlaskSecurityAdapter(app)
    
    # Create security routes
    security.create_routes(app)
    
    @app.route('/api/users', methods=['GET'])
    @security.protect(app_id='webapp_frontend', operation='SELECT')
    def get_users():
        is_auth, results, reason = security.execute("SELECT * FROM users")
        
        if is_auth:
            return jsonify({'users': results}), 200
        else:
            return jsonify({'error': reason, 'fake_data': results}), 403
    
    return app


if __name__ == '__main__':
    app = create_protected_app()
    app.run(debug=True, port=5000)
