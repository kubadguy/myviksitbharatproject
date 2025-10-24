"""
Simple Flask App - NO FIREWALL IMPORTS NEEDED!
This app uses sqlite3 normally, but if the transparent wrapper
is installed via the GUI, it gets automatic protection.
"""
from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

# Database path - use the real database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'real_database.db')

@app.route('/')
def home():
    return jsonify({
        'app': 'Simple Flask App',
        'message': 'This app uses normal sqlite3 - no firewall imports!',
        'endpoints': {
            '/users': 'GET - List all users',
            '/user/<id>': 'GET - Get user by ID',
            '/inject': 'GET - Try SQL injection',
            '/stats': 'GET - Get database stats'
        },
        'note': 'If connected via GUI, queries are automatically protected!'
    })

@app.route('/users')
def get_users():
    """Get all users - NORMAL sqlite3 code"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        conn.close()
        
        users = []
        for row in results:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'balance': row[4]
            })
        
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/user/<int:user_id>')
def get_user(user_id):
    """Get user by ID - NORMAL sqlite3 code"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'balance': row[4]
            }
            return jsonify({
                'success': True,
                'data': user
            })
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/inject')
def sql_injection():
    """
    Test SQL injection - THIS SHOULD BE BLOCKED!
    If transparent wrapper is installed, this returns fake honeypot data
    """
    try:
        # Classic SQL injection attack
        malicious_query = "SELECT * FROM users WHERE username='admin' OR '1'='1'"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(malicious_query)
        results = cursor.fetchall()
        conn.close()
        
        users = []
        for row in results:
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'balance': row[4]
            })
        
        return jsonify({
            'success': True,
            'query': malicious_query,
            'data': users,
            'warning': 'If protection is active, this is FAKE honeypot data!',
            'check': 'Look at the GUI dashboard - was this blocked?'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Query might have been blocked by firewall'
        }), 403

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        # Get total balance
        cursor.execute("SELECT SUM(balance) FROM users")
        total_balance = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': user_count,
                'total_balance': total_balance
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/create_user', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        balance = data.get('balance', 0.0)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, balance) VALUES (?, ?, ?, ?)",
            (username, email, password, balance)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  SIMPLE FLASK APP - NO FIREWALL IMPORTS")
    print("="*70)
    print("\nThis app uses normal sqlite3 code with NO firewall imports!")
    print("\nSteps to enable protection:")
    print("  1. Open the GUI: python src/main.py gui")
    print("  2. Go to 'Database Connections' tab")
    print("  3. Select SQLite and browse to src/data/real_database.db")
    print("  4. Set App ID: flask_app")
    print("  5. Click 'Connect'")
    print("  6. Now this Flask app is AUTOMATICALLY protected!")
    print("\nEndpoints:")
    print("  GET  http://127.0.0.1:5000/users    - List users")
    print("  GET  http://127.0.0.1:5000/inject   - Try SQL injection (will be blocked!)")
    print("  GET  http://127.0.0.1:5000/stats    - Get stats")
    print("\nStarting server...")
    print("="*70 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)