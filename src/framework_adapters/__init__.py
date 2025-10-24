"""
Framework adapters for integrating the security system with various web frameworks
"""

from .flask_adapter import FlaskSecurityAdapter
from .django_adapter import DjangoSecurityMiddleware
from .fastapi_adapter import FastAPISecurityMiddleware

__all__ = [
    'FlaskSecurityAdapter',
    'DjangoSecurityMiddleware',
    'FastAPISecurityMiddleware',
]
