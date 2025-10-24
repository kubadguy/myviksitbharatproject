# Transparent Database Firewall - Complete Guide

## Overview

This database firewall **transparently intercepts ALL database queries** from your applications **without them knowing**. It checks each query for security violations, SQL injection, unauthorized access, and more.

Your frameworks (FastAPI, Django, Flask) and applications work **exactly as before** - they have **no idea** the firewall exists!

---

## 🔥 How It Works

### 1. **Connection Interception** (Transparent Layer)
When your app tries to connect to a database, it connects through the firewall wrapper instead:

```python
# ❌ Old way (direct, unprotected)
conn = sqlite3.connect('database.db')

# ✅ New way (transparent firewall protection)
conn = secure_db.connect('database.db', app_id='my_app')
# Your app uses 'conn' EXACTLY the same way - no changes needed!
```

### 2. **Query Interception** (Automatic)
Every query is intercepted and checked:
- SQL injection patterns
- Access control rules (IP, time windows, permissions)
- Suspicious behavior
- Rate limiting

### 3. **Real-time Monitoring**
All queries are logged and displayed in the GUI:
- See EVERY query in real-time
- Filter by allowed/blocked
- Export audit logs
- View execution times

---

## 🚀 Quick Start

### Step 1: Initialize the Firewall

```python
from database_protection.secure_db_wrapper import initialize_secure_database

# Initialize once at app startup
secure_db = initialize_secure_database()
```

### Step 2: Use Secure Connections

#### **SQLite**
```python
# Replace sqlite3.connect() with secure_db.connect()
conn = secure_db.connect('myapp.db', app_id='my_app', ip_address='127.0.0.1')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
results = cursor.fetchall()
conn.close()
```

#### **PostgreSQL**
```python
conn = secure_db.connect_postgresql(
    host='localhost',
    database='mydb',
    user='dbuser',
    password='dbpass',
    app_id='my_app',
    ip_address='127.0.0.1'
)
# Use it exactly like psycopg2!
```

#### **MySQL**
```python
conn = secure_db.connect_mysql(
    host='localhost',
    database='mydb',
    user='dbuser',
    password='dbpass',
    app_id='my_app',
    ip_address='127.0.0.1'
)
# Use it exactly like mysql.connector!
```

---

## 📱 Framework Integration (Fully Transparent)

### **FastAPI Example**

```python
import sys
import os
from fastapi import FastAPI, Request
from database_protection.secure_db_wrapper import initialize_secure_database

app = FastAPI()

# Initialize firewall ONCE
secure_db = initialize_secure_database()

def get_db(request: Request):
    """Get database connection with automatic firewall protection"""
    ip = request.client.host
    conn = secure_db.connect('myapp.db', app_id='fastapi_app', ip_address=ip)
    return conn

@app.get("/users")
async def get_users(request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    
    # This query is AUTOMATICALLY checked by the firewall!
    cursor.execute("SELECT id, username, email FROM users")
    
    users = cursor.fetchall()
    conn.close()
    return {"users": users}

@app.get("/search")
async def search_users(q: str, request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    
    # SQL injection attempts are AUTOMATICALLY blocked!
    # Bad queries like: q = "' OR 1=1--" will be caught
    cursor.execute(f"SELECT * FROM users WHERE username = '{q}'")
    
    results = cursor.fetchall()
    conn.close()
    return {"results": results}
```

**The FastAPI app has NO IDEA the firewall exists!** It just uses the database connection normally.

---

### **Django Example**

Create a custom database backend:

```python
# myapp/db_backends/secure_sqlite.py
from django.db.backends.sqlite3 import base
from database_protection.secure_db_wrapper import initialize_secure_database

secure_db = initialize_secure_database()

class DatabaseWrapper(base.DatabaseWrapper):
    def get_new_connection(self, conn_params):
        # Intercept connection creation
        database = conn_params.get('NAME')
        return secure_db.connect(database, app_id='django_app', ip_address='127.0.0.1')
```

Then in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'myapp.db_backends.secure_sqlite',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Django now uses the firewall for ALL database queries - completely transparent!**

---

### **Flask Example**

```python
from flask import Flask, request, g
from database_protection.secure_db_wrapper import initialize_secure_database

app = Flask(__name__)
secure_db = initialize_secure_database()

def get_db():
    if 'db' not in g:
        g.db = secure_db.connect(
            'myapp.db',
            app_id='flask_app',
            ip_address=request.remote_addr
        )
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/users')
def users():
    conn = get_db()
    cursor = conn.cursor()
    
    # Firewall automatically checks this!
    cursor.execute("SELECT * FROM users")
    
    return {'users': cursor.fetchall()}
```

---

## 🛡️ Network Proxy Mode (For Remote Databases)

For PostgreSQL/MySQL servers, you can run a **transparent proxy** that sits between your app and the database:

### Start the Proxy

```bash
# For PostgreSQL (real DB on port 5432, proxy on 5433)
python -m src.database_protection.proxy_server \
    --db-type=postgresql \
    --listen-port=5433 \
    --target-host=localhost \
    --target-port=5432

# For MySQL (real DB on port 3306, proxy on 3307)
python -m src.database_protection.proxy_server \
    --db-type=mysql \
    --listen-port=3307 \
    --target-host=localhost \
    --target-port=3306
```

### Connect Through Proxy

```python
# Instead of connecting to localhost:5432
# Connect to localhost:5433 (the proxy)
conn = psycopg2.connect(
    host='localhost',
    port=5433,  # Proxy port!
    database='mydb',
    user='user',
    password='pass'
)

# The proxy intercepts ALL queries transparently!
# Your app doesn't know the firewall exists
```

---

## 📊 Real-Time Query Monitoring (GUI)

### Launch the Dashboard

```bash
python src/gui/enhanced_main_window.py
```

### Features

1. **📊 Query Data Tab** - NEW!
   - See ALL queries in real-time
   - Filter: All / Allowed / Blocked
   - View execution times
   - Export query history

2. **📈 Dashboard Tab**
   - Live statistics
   - Threat detection
   - System health

3. **🔍 Query Testing Tab**
   - Test queries manually
   - See firewall decisions
   - Debug access rules

4. **📋 Security Logs Tab**
   - View security violations
   - Intrusion attempts
   - Alert history

---

## ⚙️ Configuration

### Access Control Rules

Edit `src/config/database_config.py`:

```python
AUTHORIZED_APPS = {
    'fastapi_app': {
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'time_windows': [(9, 17)],  # 9 AM - 5 PM
        'ip_whitelist': ['127.0.0.1', '192.168.1.*'],
    },
    'django_app': {
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'time_windows': [(0, 23)],  # Always
        'ip_whitelist': ['*'],  # Any IP
    },
}
```

### Security Settings

Edit `src/config/settings.py`:

```python
class Settings:
    REAL_DB_PATH = 'data/real_database.db'
    HONEYPOT_DB_PATH = 'data/honeypot.db'
    
    # Alert settings
    ENABLE_EMAIL_ALERTS = False
    ENABLE_SMS_ALERTS = False
```

---

## 🧪 Testing

### Test with Sample Apps

```bash
# 1. Start the FastAPI demo (with firewall protection)
cd fastapi_demo
python app.py

# 2. Try legitimate queries
curl http://localhost:8000/products

# 3. Try SQL injection (will be BLOCKED)
curl "http://localhost:8000/search?q=' OR 1=1--"

# 4. Watch the GUI - you'll see ALL queries!
```

### Test with Proxy

```bash
# 1. Start PostgreSQL proxy
python -m src.database_protection.proxy_server --db-type=postgresql

# 2. Connect any PostgreSQL client to localhost:5433
psql -h localhost -p 5433 -U user -d mydb

# 3. Run queries - they're ALL intercepted!
```

---

## 🎯 Key Features

### ✅ What Gets Intercepted

- **ALL database queries** (SELECT, INSERT, UPDATE, DELETE)
- **Connection attempts**
- **Parameter values** (for injection detection)
- **Timing and metadata**

### ✅ What Gets Checked

- **SQL Injection patterns** (union, or 1=1, etc.)
- **Access control** (app authorization, IP whitelist, time windows)
- **Operation permissions** (can this app DELETE?)
- **Rate limiting** (coming soon)

### ✅ What You See

- **Real-time query log** with timestamps
- **Execution times** for each query
- **Allow/block decisions** with reasons
- **Statistics** (total queries, block rate, etc.)
- **Export capabilities** (JSON logs)

---

## 🔐 Security Benefits

1. **Zero Trust Architecture**
   - Every query is checked, even from "trusted" apps
   - Defense in depth

2. **SQL Injection Protection**
   - Pattern-based detection
   - Automatic blocking

3. **Access Control**
   - Time-based restrictions
   - IP whitelisting
   - Operation-level permissions

4. **Honeypot**
   - Attackers get fake data
   - Real data stays safe
   - Collect attack intelligence

5. **Audit Trail**
   - Complete query history
   - Security incident tracking
   - Compliance reporting

---

## 📝 Example: Complete FastAPI App

See `fastapi_demo/app.py` for a working example. Key points:

```python
# 1. Initialize firewall ONCE at startup
secure_db = initialize_secure_database()

# 2. Use in connection function
def get_db(request: Request):
    return secure_db.connect('shop.db', app_id='shop_api', 
                             ip_address=request.client.host)

# 3. Use normally in routes - framework doesn't know about firewall!
@app.get("/products")
async def get_products(request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")  # Intercepted!
    return {"products": cursor.fetchall()}
```

---

## 🎉 Summary

**Your applications work EXACTLY as before**, but now:
- ✅ All queries are intercepted
- ✅ Security checks are automatic
- ✅ Real-time monitoring in GUI
- ✅ Complete audit trail
- ✅ SQL injection protection
- ✅ Access control enforcement

**The framework/application has NO IDEA the firewall exists!**

---

## 🚀 Next Steps

1. Run `python src/gui/enhanced_main_window.py` to see the dashboard
2. Run your FastAPI/Flask/Django app with the secure wrapper
3. Watch the **Query Data** tab to see ALL queries in real-time!
4. Try SQL injection attacks - watch them get BLOCKED!

**Happy securing! 🔒**
