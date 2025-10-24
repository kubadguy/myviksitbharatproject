"""
Django settings for security demo project.
"""
import os
import sys

# Add src to path for security system imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, '..', 'src'))

SECRET_KEY = 'demo-secret-key-do-not-use-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Our security middleware
    'framework_adapters.django_adapter.DjangoSecurityMiddleware',
]

ROOT_URLCONF = 'urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'demo_db.sqlite3'),
    }
}

# Security system configuration
DB_SECURITY_CONFIG = {
    'enabled': True,
    'app_id': 'django_demo',
}

# Disable CSRF for demo purposes
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m.lower()]

USE_TZ = True
