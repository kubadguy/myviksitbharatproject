AUTHORIZED_APPS = {
    'webapp_frontend': {
        'time_windows': [(9, 17)],  # 9 AM - 5 PM
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'ip_whitelist': ['192.168.1.0/24']
    },
    'backup_service': {
        'time_windows': [(2, 4)],  # 2 AM - 4 AM
        'allowed_operations': ['SELECT'],
        'ip_whitelist': ['10.0.0.5']
    },
    'admin_panel': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ip_whitelist': ['192.168.1.100']
    },
    # Demo applications - allow from localhost for testing
    'shop_api': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ip_whitelist': ['127.0.0.1', '::1']
    },
    'demo_app': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE'],
        'ip_whitelist': ['127.0.0.1', '::1']
    },
    'fastapi_app': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'ip_whitelist': ['*']  # Allow from any IP for demo
    },
    'flask_app': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'ip_whitelist': ['*']
    },
    'django_app': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ip_whitelist': ['*']
    }
}
