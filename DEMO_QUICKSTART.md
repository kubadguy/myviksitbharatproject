# 🚀 Django Demo - Quick Start Guide

## Run the Demo in 3 Steps!

### Step 1: Initialize Database
```bash
cd demo_django_project
python init_db.py
```

You should see:
```
✅ Database initialized: demo_db.sqlite3
✅ Created 5 users
```

### Step 2: Start Django Server
```bash
python manage.py
```

Server will start on http://localhost:8000

### Step 3: Test It!

**Option A - Legitimate User (New Terminal)**
```bash
cd demo_django_project
python legitimate_user.py
```

**Option B - Attacker (Another Terminal)**
```bash
cd demo_django_project
python attacker.py
```

**Option C - Browser**
Visit http://localhost:8000

## 📊 What You'll See

### Legitimate User Results ✅
```
============================================================
  1. GET /users/ - Fetch all users
============================================================
Status Code: 200
✅ Success! Retrieved 5 users
   - john_doe (john@example.com) - user
   - jane_smith (jane@example.com) - user
   - admin (admin@example.com) - admin
```

### Attacker Results ❌
```
======================================================================
🔴 ATTACK #1: Classic SQL Injection - OR 1=1
======================================================================
Target: /search/
Params: {'name': "' OR '1'='1"}
Status Code: 403
🛡️  BLOCKED by Security System!
Reason: SQL injection pattern detected: (\bOR\b.*=.*)
📦 Received HONEYPOT data (not real database)
```

### Statistics
```
📊 Security Statistics:
   Total Queries: 15
   Authorized: 5
   Blocked: 10
   Block Rate: 66.7%
   Unique IPs: 1
```

## 🎯 Key Points

1. **Legitimate users work normally** - No impact on user experience
2. **Attackers are blocked** - SQL injection attempts fail
3. **Fake data returned** - Attackers get honeypot data, not real data
4. **Everything is logged** - Full audit trail maintained

## 🛡️ What's Protected

The demo shows protection against:
- ✅ SQL Injection (OR 1=1)
- ✅ UNION-based attacks
- ✅ Comment bypass (--) 
- ✅ Stacked queries
- ✅ Time-based blind SQLi
- ✅ Error-based SQLi
- ✅ And more...

## 📝 Files Overview

- `init_db.py` - Creates demo database with 5 users
- `manage.py` - Starts Django development server
- `legitimate_user.py` - Simulates normal user (5 requests)
- `attacker.py` - Simulates attacker (10 SQL injection attempts)
- `views.py` - Django views protected by security system
- `settings.py` - Django settings with security middleware

## 🔍 Try Different Scenarios

### Scenario 1: Mixed Traffic
Run both legitimate and attack traffic simultaneously to see how the system handles mixed requests.

### Scenario 2: Custom Attacks
Modify `attacker.py` to try your own SQL injection patterns.

### Scenario 3: Configuration Changes
Edit `../src/config/database_config.py` to adjust security rules.

## 🎓 How It Works

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│ Security Middleware  │ ◄─ Checks every query
└──────┬───────────────┘
       │
       ├─► ✅ Legitimate? ──► Real Database ──► User
       │
       └─► ❌ Malicious?  ──► Honeypot ──────► Attacker
                                  +
                             Log Attack
```

## 🏆 Expected Results

After running both scripts:
- **Legitimate user**: 5/5 requests successful (100%)
- **Attacker**: 0/10 attacks successful (0%, all blocked)
- **System status**: Working perfectly! 🎉

## 🐛 Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'django'`  
**Solution**: `pip install django`

**Problem**: `Address already in use`  
**Solution**: Kill existing Django process or use different port

**Problem**: `Cannot connect to server`  
**Solution**: Make sure Django server is running first

**Problem**: Import errors  
**Solution**: Make sure you're in `demo_django_project` directory

## 📚 Next Steps

1. ✅ Run the demo
2. 📖 Read the full documentation: `demo_django_project/README.md`
3. 🔧 Try integrating with your own Django project
4. 📊 Explore the security statistics
5. 🛠️ Customize the security rules

## 💡 Tips

- Watch the terminal where Django is running to see security alerts in real-time
- Use `curl` to test individual endpoints
- Check `/stats/` endpoint to see aggregated statistics
- The database is recreated each time you run `init_db.py`

## 🎉 Success!

If you see:
- ✅ Legitimate requests: All succeed
- ❌ Attack requests: All blocked
- 📊 Statistics: Show correct counts

**The security system is working!** You've successfully demonstrated that:
- Normal users can use your application
- Attackers are automatically blocked
- No code changes needed (just middleware!)
- Complete visibility into security events

---

**Ready for production? Check out the full integration guide!**
