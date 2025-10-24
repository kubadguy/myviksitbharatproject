# Django Security System Demo

This demo project shows the database security system in action with a real Django application.

## 🎯 What This Demo Shows

- ✅ **Legitimate users** can access the database normally
- ❌ **Attackers** attempting SQL injection are **blocked** and redirected to honeypot
- 📊 **Real-time statistics** track all security events
- 🛡️ **Complete protection** without changing existing code

## 📁 Project Structure

```
demo_django_project/
├── settings.py          # Django settings with security middleware
├── urls.py              # URL routing
├── views.py             # Views with security protection
├── init_db.py           # Database initialization
├── manage.py            # Django runner
├── legitimate_user.py   # Simulates normal user
├── attacker.py          # Simulates SQL injection attacks
└── README.md            # This file
```

## 🚀 Quick Start

### Step 1: Install Dependencies

Make sure Django is installed:
```bash
pip install django
```

### Step 2: Initialize Database

```bash
cd demo_django_project
python init_db.py
```

Expected output:
```
✅ Database initialized: demo_db.sqlite3
✅ Created 5 users

📋 Users in database:
  ID: 1, Username: john_doe, Email: john@example.com, Role: user
  ID: 2, Username: jane_smith, Email: jane@example.com, Role: user
  ID: 3, Username: admin, Email: admin@example.com, Role: admin
  ID: 4, Username: bob_wilson, Email: bob@example.com, Role: user
  ID: 5, Username: alice_johnson, Email: alice@example.com, Role: moderator
```

### Step 3: Start Django Server

```bash
python manage.py
```

The server will start on http://localhost:8000

### Step 4: Test Legitimate User

In a **new terminal**:
```bash
cd demo_django_project
python legitimate_user.py
```

This will make 5 normal requests - all should succeed! ✅

### Step 5: Run Attack Simulation

In another terminal:
```bash
cd demo_django_project
python attacker.py
```

This will attempt 10 SQL injection attacks - all should be blocked! 🛡️

## 🔍 What Happens

### Legitimate User Flow
```
User → Django → Security Check ✅ → Real Database → User
```

1. User requests `/users/`
2. Security system checks: App ID, IP, operation
3. ✅ **AUTHORIZED** - Query executes on real database
4. User receives real data

### Attacker Flow
```
Attacker → Django → Security Check ❌ → Honeypot → Attacker
```

1. Attacker attempts SQL injection
2. Security system detects malicious pattern
3. ❌ **BLOCKED** - Query redirected to honeypot
4. Attacker receives fake data
5. Security event logged

## 📊 Available Endpoints

### API Endpoints

- `GET /` - Home page with documentation
- `GET /users/` - List all users (protected)
- `GET /user/<id>/` - Get specific user (protected)
- `GET /search/?name=<query>` - Search users (protected, vulnerable without security)
- `GET /stats/` - Security statistics

### Test with cURL

```bash
# Legitimate request
curl http://localhost:8000/users/

# SQL injection attempt (will be blocked)
curl "http://localhost:8000/search/?name=' OR '1'='1"

# View statistics
curl http://localhost:8000/stats/
```

## 🛡️ Security Features Demonstrated

### 1. SQL Injection Detection
The system detects and blocks:
- Classic SQLi (`OR 1=1`)
- UNION-based attacks
- Comment-based bypass
- Stacked queries
- Time-based blind SQLi
- And more...

### 2. Honeypot Redirection
Attackers receive **fake data** from honeypot instead of real database.

### 3. Security Logging
All blocked attempts are logged with:
- IP address
- Attack type
- Query attempted
- Timestamp

### 4. Real-time Statistics
View current security status:
- Total queries
- Blocked vs authorized
- Unique IP addresses
- Recent blocks

## 🧪 Testing Scenarios

### Scenario 1: Normal Operation
```bash
python legitimate_user.py
```

**Expected Result:**
- All 5 requests succeed
- Data from real database returned
- No security alerts

### Scenario 2: SQL Injection Attack
```bash
python attacker.py
```

**Expected Result:**
- All 10 attacks blocked
- Fake honeypot data returned
- Security alerts logged
- 100% block rate

### Scenario 3: Mixed Traffic
```bash
# Terminal 1: Start server
python manage.py

# Terminal 2: Legitimate traffic
python legitimate_user.py

# Terminal 3: Attack traffic
python attacker.py

# Terminal 4: Check stats
curl http://localhost:8000/stats/
```

**Expected Result:**
- Legitimate queries: ✅ Authorized
- Attack queries: ❌ Blocked
- Statistics show mixed traffic

## 📈 Viewing Results

### In Browser
Visit http://localhost:8000/stats/ to see:
- Total queries
- Block rate
- Recent blocked attacks

### In Code
Check the security logs:
```python
# In Django shell or view
from framework_adapters.django_adapter import DjangoSecurityMiddleware

logs = request.db_security.get_logs()
for log in logs:
    print(f"{log['ip_address']}: {log['reason']}")
```

## 🔧 Customization

### Add More Users
Edit `init_db.py` and add users to the list:
```python
users = [
    ('new_user', 'new@example.com', 'user', 'password_hash'),
    # ... existing users
]
```

### Change Security Rules
Edit `src/config/database_config.py`:
```python
AUTHORIZED_APPS = {
    'django_demo': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'ip_whitelist': ['127.0.0.1']
    }
}
```

### Add More Endpoints
Edit `views.py` to add new protected endpoints:
```python
@protect_query(app_id='django_demo', operation='INSERT')
def create_user(request):
    # Your code here
    pass
```

## 🐛 Troubleshooting

### Django Not Installed
```bash
pip install django
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

### Cannot Connect Errors
Make sure the Django server is running before running test scripts.

### Import Errors
Make sure you're in the correct directory:
```bash
cd demo_django_project
```

## 📚 Learn More

- Main README: `../README.md`
- Integration Guide: `../INTEGRATION_GUIDE.md`
- Enterprise Features: `../ENTERPRISE_FEATURES.md`

## 🎓 Key Takeaways

1. ✅ **No Code Changes Required** - Just add the middleware
2. 🛡️ **Automatic Protection** - All queries are checked
3. 📊 **Full Visibility** - Complete audit trail
4. 🎯 **Zero False Positives** - Legitimate users unaffected
5. 🔒 **Defense in Depth** - Honeypot + detection + logging

## 🏆 Success Criteria

After running the demo, you should see:

- ✅ Legitimate users: 100% success rate
- ❌ Attackers: 100% block rate
- 📊 Statistics showing mixed traffic
- 🛡️ No real data leaked to attackers
- 📝 All attacks logged

**The security system works!** 🎉
