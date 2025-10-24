"""
Views for security demo - integrated with security system
"""
from django.http import JsonResponse, HttpResponse
from framework_adapters.django_adapter import protect_query
import sqlite3
import os


def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'demo_db.sqlite3')
    return sqlite3.connect(db_path)


def home(request):
    """Home page with API documentation"""
    return HttpResponse("""
    <html>
    <head><title>Secure Django Demo</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🔒 Secure Django API Demo</h1>
        <p>This demo shows legitimate vs malicious queries being handled by the security system.</p>
        
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/users/">/users/</a> - Get all users (protected)</li>
            <li><a href="/user/1/">/user/1/</a> - Get user by ID (protected)</li>
            <li><a href="/search/?name=john">/search/?name=john</a> - Search users (protected)</li>
            <li><a href="/stats/">/stats/</a> - Security statistics</li>
        </ul>
        
        <h2>Test Commands:</h2>
        <pre>
# Legitimate request
curl http://localhost:8000/users/

# Attack simulation
python attacker.py
        </pre>
    </body>
    </html>
    """)


@protect_query(app_id='django_demo', operation='SELECT')
def get_users(request):
    """Get all users - Protected by security system"""
    query = "SELECT id, username, email, role FROM users"
    
    # Execute through security system
    is_auth, results, reason = request.db_security.execute_query(
        request,
        app_id='django_demo',
        operation='SELECT',
        query=query
    )
    
    if is_auth:
        # Convert tuples to dictionaries for JSON response
        users = []
        for row in results:
            if isinstance(row, dict):
                users.append(row)
            else:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'role': row[3]
                })
        
        return JsonResponse({
            'success': True,
            'users': users,
            'message': 'Query authorized and executed'
        })
    else:
        return JsonResponse({
            'success': False,
            'error': reason,
            'message': 'Query blocked by security system',
            'fake_data': results  # Honeypot data
        }, status=403)


@protect_query(app_id='django_demo', operation='SELECT')
def get_user(request, user_id):
    """Get single user by ID - Protected"""
    query = f"SELECT id, username, email, role FROM users WHERE id = {user_id}"
    
    is_auth, results, reason = request.db_security.execute_query(
        request,
        app_id='django_demo',
        operation='SELECT',
        query=query
    )
    
    if is_auth:
        if results:
            row = results[0]
            user = {
                'id': row[0] if not isinstance(row, dict) else row['id'],
                'username': row[1] if not isinstance(row, dict) else row['username'],
                'email': row[2] if not isinstance(row, dict) else row['email'],
                'role': row[3] if not isinstance(row, dict) else row['role']
            }
            return JsonResponse({'success': True, 'user': user})
        else:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    else:
        return JsonResponse({
            'success': False,
            'error': reason,
            'fake_data': results
        }, status=403)


@protect_query(app_id='django_demo', operation='SELECT')
def search_users(request):
    """Search users by name - Protected and vulnerable to SQLi if not protected"""
    search_term = request.GET.get('name', '')
    
    # This query is vulnerable to SQL injection without our protection
    query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{search_term}%'"
    
    is_auth, results, reason = request.db_security.execute_query(
        request,
        app_id='django_demo',
        operation='SELECT',
        query=query
    )
    
    if is_auth:
        users = []
        for row in results:
            if isinstance(row, dict):
                users.append(row)
            else:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'role': row[3]
                })
        
        return JsonResponse({
            'success': True,
            'users': users,
            'search_term': search_term
        })
    else:
        return JsonResponse({
            'success': False,
            'error': reason,
            'message': f'Security system blocked malicious query',
            'attempted_search': search_term
        }, status=403)


def get_stats(request):
    """Get security statistics"""
    logs = request.db_security.get_logs()
    
    total = len(logs)
    blocked = sum(1 for log in logs if log['action'] == 'REDIRECTED_TO_HONEYPOT')
    unique_ips = len(set(log['ip_address'] for log in logs))
    
    recent_blocks = [
        {
            'ip': log['ip_address'],
            'reason': log['reason'],
            'query': log['query'][:100]
        }
        for log in logs[-5:] if log['action'] == 'REDIRECTED_TO_HONEYPOT'
    ]
    
    return JsonResponse({
        'statistics': {
            'total_queries': total,
            'blocked_queries': blocked,
            'authorized_queries': total - blocked,
            'unique_ips': unique_ips,
            'block_rate': f"{(blocked/total*100):.1f}%" if total > 0 else "0%"
        },
        'recent_blocks': recent_blocks
    })
