"""
Django runner for the demo project
"""
import os
import sys

if __name__ == '__main__':
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

    import django
    from django.core.management import execute_from_command_line

    # Initialize Django
    django.setup()

    # Run development server
    execute_from_command_line([sys.argv[0], 'runserver', '8000'])
