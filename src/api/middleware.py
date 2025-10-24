from flask import request, jsonify
from functools import wraps
import time
from typing import Callable


class SecurityMiddleware:
    def __init__(self):
        self.rate_limits = {}
        self.blocked_ips = set()

    def rate_limit(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Rate limiting decorator
        """
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                ip = request.remote_addr
                current_time = time.time()

                # Initialize tracking for this IP
                if ip not in self.rate_limits:
                    self.rate_limits[ip] = []

                # Clean old requests outside the window
                self.rate_limits[ip] = [
                    req_time for req_time in self.rate_limits[ip]
                    if current_time - req_time < window_seconds
                ]

                # Check rate limit
                if len(self.rate_limits[ip]) >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {max_requests} requests per {window_seconds} seconds'
                    }), 429

                # Record this request
                self.rate_limits[ip].append(current_time)

                return f(*args, **kwargs)
            return wrapper
        return decorator

    def require_api_key(self, f: Callable):
        """
        API key authentication decorator
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'API key is missing'
                }), 401

            # In production, validate against a database or configuration
            # For now, we'll accept any non-empty key
            if not self._validate_api_key(api_key):
                return jsonify({
                    'error': 'Authentication failed',
                    'message': 'Invalid API key'
                }), 403

            return f(*args, **kwargs)
        return wrapper

    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key (placeholder implementation)
        In production, check against database or configuration
        """
        # Placeholder: accept any non-empty key for demo
        return len(api_key) > 0

    def ip_whitelist(self, allowed_ips: list):
        """
        IP whitelist decorator
        """
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                ip = request.remote_addr
                
                if ip not in allowed_ips:
                    return jsonify({
                        'error': 'Access denied',
                        'message': 'Your IP is not whitelisted'
                    }), 403

                return f(*args, **kwargs)
            return wrapper
        return decorator

    def block_ip(self, ip: str):
        """Add an IP to the blocked list"""
        self.blocked_ips.add(ip)

    def unblock_ip(self, ip: str):
        """Remove an IP from the blocked list"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)

    def check_blocked_ip(self, f: Callable):
        """
        Check if IP is blocked decorator
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            
            if ip in self.blocked_ips:
                return jsonify({
                    'error': 'Access denied',
                    'message': 'Your IP has been blocked'
                }), 403

            return f(*args, **kwargs)
        return wrapper

    def log_request(self, f: Callable):
        """
        Request logging decorator
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            method = request.method
            path = request.path
            
            print(f"[API] {method} {path} from {ip}")
            
            result = f(*args, **kwargs)
            
            return result
        return wrapper

    def cors_headers(self, f: Callable):
        """
        Add CORS headers decorator
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                data, status_code = response
                return data, status_code, {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, X-API-Key'
                }
            
            return response
        return wrapper


# Global middleware instance
middleware = SecurityMiddleware()
