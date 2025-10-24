# FastAPI Demo with TRANSPARENT Database Security

A real-world e-commerce API demonstrating **completely transparent** database security.

## 🎯 Key Concept: ZERO Application Changes

The FastAPI application has **ABSOLUTELY NO KNOWLEDGE** of the security system!

- ❌ No security imports in app code
- ❌ No authentication decorators
- ❌ No security middleware in the app
- ✅ App uses normal `sqlite3` connections
- ✅ Security is **100% transparent** at the database driver level
- ✅ Protection is controlled **externally via dashboard**

## Architecture

```
┌──────────────┐
│ FastAPI App  │ ← Has NO knowledge of security!
│  (app.py)    │ ← Just uses secure_db.connect()
└──────┬───────┘
       │
       ↓
┌──────────────────────┐
│ Secure DB Wrapper    │ ← Transparent interception
│ (secure_db_wrapper)  │ ← Checks every query
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ Security Firewall    │ ← Registered apps only!
│ (firewall.py)        │ ← Blocks SQL injection
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   SQLite Database    │
│    (shop.db)         │
└──────────────────────┘

┌──────────────────────┐
│   Dashboard          │ ← Register/manage apps
│ (dashboard.py)       │ ← View attack logs
└──────────────────────┘
```

## Quick Start

### 1. Initialize Database
```bash
cd fastapi_demo
python init_db.py
```

### 2. Register App in Dashboard (REQUIRED!)
```bash
cd ../dashboard
python dashboard.py
```
Then register the app:
- App ID: `shop_api`
- App Name: `Shop API`
- Enable it!

### 3. Start FastAPI Server
```bash
cd ../fastapi_demo
python app.py
```

### 4. Test Normal User (Should work)
```bash
python customer.py
```

### 5. Simulate Attacks (Should be blocked)
```bash
python hacker.py
```

## How It Works

### Application Side (app.py)

The app just uses `secure_db.connect()` instead of `sqlite3.connect()`:

```python
# Initialize security wrapper once at startup
secure_db = initialize_secure_database('security.db')

# Then use it exactly like sqlite3.connect()
def get_db(request):
    conn = secure_db.connect(
        'shop.db',
        app_id='shop_api',
        ip_address=request.client.host
    )
    return conn
```

**That's it!** The app doesn't know anything else about security.

### Security Side (transparent wrapper)

Every query is intercepted and checked:

1. **Is the app registered?** → Check dashboard database
2. **Is the query malicious?** → Pattern matching, ML detection
3. **Rate limiting?** → Check IP/app query frequency
4. **Allow or Block** → Real data vs honeypot data

### Dashboard Side

- Register/unregister apps
- Enable/disable protection per app
- View attack logs in real-time
- Manage security policies

## Endpoints

### Public
- `GET /` - Home page
- `GET /products` - List products
- `GET /product/{id}` - Product details

### Protected (Need dashboard registration)
- `GET /users` - List users
- `GET /user/{id}` - User by ID (vulnerable!)
- `GET /search?q=...` - Search (intentionally vulnerable!)
- `GET /admin/stats` - Statistics

## Attack Simulation

The `hacker.py` script tries 12 different SQL injection attacks:

1. Classic injection (`' OR '1'='1`)
2. UNION-based injection
3. Comment bypass (`admin'--`)
4. Boolean blind SQLi
5. DROP TABLE attack
6. Admin credential extraction
7. Time-based blind SQLi
8. Error-based SQLi
9. Subquery injection
10. Schema extraction
11. Hex encoding
12. Multi-statement attack

**Expected Result:** All attacks blocked with 403 errors!

## Why This Architecture?

### Traditional Approach ❌
```python
@app.get("/users")
@require_auth  # ← App knows about security
@check_sql_injection  # ← App implements security
def get_users():
    ...
```

### Our Approach ✅
```python
@app.get("/users")
def get_users(request):
    conn = secure_db.connect(...)  # ← Security is transparent!
    # Rest is normal code
```

### Benefits

1. **Zero Refactoring** - Existing apps work with minimal changes
2. **Centralized Control** - Manage security from dashboard
3. **App Independence** - Security and app are decoupled
4. **Retroactive Protection** - Protect legacy code without changes
5. **Universal** - Works with any Python app using SQLite

## Testing

```bash
# Legitimate customer (should work)
python customer.py

# Attacker (should be blocked)
python hacker.py

# Check logs in dashboard
cd ../dashboard
python dashboard.py
```

## Files

- `app.py` - FastAPI application (no security knowledge!)
- `init_db.py` - Database initialization
- `customer.py` - Legitimate user simulation
- `hacker.py` - Attack simulation
- `shop.db` - Application database
- `../security.db` - Security system database (managed by dashboard)
