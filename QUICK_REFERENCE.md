# Quick Reference - Transparent Database Firewall

## 🔥 What You Built

A **transparent database firewall** that:
- ✅ Intercepts ALL database queries automatically
- ✅ Works with SQLite, PostgreSQL, MySQL
- ✅ Applications have NO IDEA it exists
- ✅ Real-time query monitoring with GUI
- ✅ Complete audit trail with timestamps
- ✅ SQL injection detection and blocking
- ✅ Access control (IP, time, permissions)

---

## 🚀 5-Minute Setup

### 1. Basic Usage (SQLite)

```python
from database_protection.secure_db_wrapper import initialize_secure_database

# Initialize once
secure_db = initialize_secure_database()

# Use like normal sqlite3 - but PROTECTED!
conn = secure_db.connect('db.sqlite', app_id='my_app', ip_address='127.0.0.1')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")  # Intercepted & checked!
results = cursor.fetchall()
```

### 2. FastAPI Integration

```python
from fastapi import FastAPI, Request
from database_protection.secure_db_wrapper import initialize_secure_database

app = FastAPI()
secure_db = initialize_secure_database()

def get_db(request: Request):
    return secure_db.connect('app.db', app_id='api', 
                             ip_address=request.client.host)

@app.get("/users")
async def users(request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")  # Protected!
    return {"users": cursor.fetchall()}
```

### 3. View All Queries (GUI)

```bash
python src/gui/enhanced_main_window.py
```

Go to **📊 Query Data** tab → See ALL queries in real-time!

---

## 📊 GUI Features

### Dashboard Tab
- Live statistics
- Threat detection
- System health

### Query Data Tab (NEW!)
- **Real-time query feed**
- Filter: All / Allowed / Blocked
- Execution times
- Export to JSON
- Auto-refresh every 2 seconds

### Query Testing Tab
- Test queries manually
- See firewall decisions
- Debug access rules

### Security Logs Tab
- Intrusion attempts
- Security violations
- Alert history

---

## 🌐 Database Support

### SQLite
```python
conn = secure_db.connect('db.sqlite', app_id='app1', ip_address='127.0.0.1')
```

### PostgreSQL
```python
conn = secure_db.connect_postgresql(
    host='localhost', port=5432, database='mydb',
    user='user', password='pass', app_id='app1', ip_address='127.0.0.1'
)
```

### MySQL
```python
conn = secure_db.connect_mysql(
    host='localhost', port=3306, database='mydb',
    user='user', password='pass', app_id='app1', ip_address='127.0.0.1'
)
```

---

## 🛡️ Network Proxy Mode

Start a transparent proxy between app and database:

```bash
# PostgreSQL proxy
python -m src.database_protection.proxy_server \
    --db-type=postgresql \
    --listen-port=5433 \
    --target-port=5432

# MySQL proxy
python -m src.database_protection.proxy_server \
    --db-type=mysql \
    --listen-port=3307 \
    --target-port=3306
```

Then connect your app to the proxy port instead!

---

## ⚙️ Configuration

### Access Control (`src/config/database_config.py`)

```python
AUTHORIZED_APPS = {
    'my_app': {
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'time_windows': [(9, 17)],  # 9 AM - 5 PM
        'ip_whitelist': ['127.0.0.1', '192.168.1.*'],
    },
}
```

### Security Settings (`src/config/settings.py`)

```python
class Settings:
    REAL_DB_PATH = 'data/real_database.db'
    HONEYPOT_DB_PATH = 'data/honeypot.db'
    ENABLE_EMAIL_ALERTS = False
    ENABLE_SMS_ALERTS = False
```

---

## 🧪 Testing

### Run Demo
```bash
python demo_transparent_firewall.py
```

### Run FastAPI Demo
```bash
cd fastapi_demo
python app.py
```

Try legitimate queries:
```bash
curl http://localhost:8000/products
```

Try SQL injection (will be blocked):
```bash
curl "http://localhost:8000/search?q=' OR 1=1--"
```

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `src/database_protection/secure_db_wrapper.py` | Transparent connection wrapper |
| `src/database_protection/proxy_server.py` | Network proxy for remote DBs |
| `src/core/firewall.py` | Main firewall logic |
| `src/core/logger.py` | Query history & logging |
| `src/gui/enhanced_main_window.py` | GUI dashboard |
| `demo_transparent_firewall.py` | Demo script |
| `TRANSPARENT_FIREWALL_GUIDE.md` | Complete documentation |

---

## 🎯 What Gets Intercepted

- ✅ ALL `SELECT` queries
- ✅ ALL `INSERT` queries
- ✅ ALL `UPDATE` queries
- ✅ ALL `DELETE` queries
- ✅ Connection attempts
- ✅ Parameter values

## 🛡️ What Gets Checked

- ✅ SQL injection patterns (OR 1=1, UNION, etc.)
- ✅ App authorization (is app registered?)
- ✅ IP whitelist (is IP allowed?)
- ✅ Time windows (is it allowed now?)
- ✅ Operation permissions (can app DELETE?)

## 📊 What You See

- ✅ Every query with timestamp
- ✅ Allowed vs Blocked status
- ✅ Execution time (ms)
- ✅ App ID and IP address
- ✅ Block reason (if blocked)
- ✅ Real-time statistics

---

## 🎉 The Magic

**Your application code stays EXACTLY THE SAME!**

Just change:
```python
# From this:
conn = sqlite3.connect('db.sqlite')

# To this:
conn = secure_db.connect('db.sqlite', app_id='my_app')
```

That's it! Now:
- ✅ All queries are intercepted
- ✅ Security checks are automatic
- ✅ Real-time monitoring works
- ✅ Audit trail is maintained
- ✅ SQL injections are blocked

**The framework doesn't know the firewall exists!**

---

## 📚 More Info

- **Complete Guide**: See `TRANSPARENT_FIREWALL_GUIDE.md`
- **README**: See `README.md`
- **Demo Script**: Run `python demo_transparent_firewall.py`
- **FastAPI Example**: See `fastapi_demo/app.py`

---

## 💡 Quick Tips

1. **Always initialize once** at app startup:
   ```python
   secure_db = initialize_secure_database()
   ```

2. **Pass the actual IP address** for access control:
   ```python
   conn = secure_db.connect(db, app_id='app', ip_address=request.client.host)
   ```

3. **Register your app** in `src/config/database_config.py`:
   ```python
   AUTHORIZED_APPS = {
       'my_app': {...}
   }
   ```

4. **Check the GUI** to see all queries in real-time!

5. **Export logs** for compliance/auditing

---

**Happy Securing! 🔒**
