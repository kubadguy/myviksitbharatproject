"""
Django adapter for integrating database security system

Installation:
    Add to settings.py:
    
    MIDDLEWARE = [
        ...
        'framework_adapters.django_adapter.DjangoSecurityMiddleware',
    ]
    
    DB_SECURITY_CONFIG = {
        'enabled': True,
        'app_id': 'django_app',
    }
"""

import sys
import os
from typing import Callable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.firewall import DatabaseFirewall


class DjangoSecurityMiddleware:
    """
    Django middleware for database security
    """
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.firewall = DatabaseFirewall()
    
    def __call__(self, request):
        # Add firewall to request
        request.db_security = self
        
        # Store request info for query execution
        request.security_ip = self.get_client_ip(request)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def execute_query(self, request, app_id: str, operation: str, query: str):
        """
        Execute a query through the security system
        
        Usage in views:
            def my_view(request):
                is_auth, results, reason = request.db_security.execute_query(
                    request,
                    app_id='my_app',
                    operation='SELECT',
                    query='SELECT * FROM users'
                )
        """
        ip_address = self.get_client_ip(request)
        
        return self.firewall.execute_query(
            app_id=app_id,
            ip_address=ip_address,
            operation=operation,
            query=query
        )
    
    def get_logs(self):
        """Get security logs"""
        return self.firewall.get_logs()


# Django view decorators
def protect_query(app_id: str, operation: str):
    """
    Decorator for Django views to protect database queries
    
    Usage:
        from framework_adapters.django_adapter import protect_query
        
        @protect_query(app_id='my_app', operation='SELECT')
        def my_view(request):
            # Access protected query execution via request
            pass
    """
    def decorator(view_func: Callable):
        def wrapper(request, *args, **kwargs):
            request.security_app_id = app_id
            request.security_operation = operation
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Django REST Framework integration
class DRFSecurityMixin:
    """
    Mixin for Django REST Framework ViewSets
    
    Usage:
        from rest_framework import viewsets
        from framework_adapters.django_adapter import DRFSecurityMixin
        
        class UserViewSet(DRFSecurityMixin, viewsets.ModelViewSet):
            security_app_id = 'api'
            security_operation = 'SELECT'
            
            def list(self, request):
                is_auth, results, reason = self.execute_secure_query(
                    'SELECT * FROM users'
                )
                return Response({'users': results})
    """
    
    security_app_id = 'unknown'
    security_operation = 'SELECT'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firewall = DatabaseFirewall()
    
    def execute_secure_query(self, query: str):
        """Execute a query through the security system"""
        request = self.request
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        return self.firewall.execute_query(
            app_id=self.security_app_id,
            ip_address=ip_address,
            operation=self.security_operation,
            query=query
        )


# Example Django views
"""
# views.py example

from django.http import JsonResponse
from framework_adapters.django_adapter import protect_query

@protect_query(app_id='webapp_frontend', operation='SELECT')
def get_users(request):
    is_auth, results, reason = request.db_security.execute_query(
        request,
        app_id=request.security_app_id,
        operation=request.security_operation,
        query='SELECT * FROM users'
    )
    
    if is_auth:
        return JsonResponse({'users': results})
    else:
        return JsonResponse({'error': reason}, status=403)

def get_security_logs(request):
    logs = request.db_security.get_logs()
    return JsonResponse({'logs': logs})
"""
