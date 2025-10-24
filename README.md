# Database Security System

A **transparent database firewall** that intercepts ALL database queries without your application knowing! Complete with honeypot functionality, intrusion detection, and real-time monitoring.

## 🔥 Key Features

- **🛡️ Transparent Query Interception**: Applications connect through the firewall wrapper - they have NO IDEA it exists!
- **📊 Real-Time Query Monitoring**: NEW! See ALL queries in a dedicated "Query Data" tab with filtering and export
- **🗄️ Multi-Database Support**: SQLite, PostgreSQL, MySQL with transparent wrappers
- **🌐 Network Proxy Mode**: Run a proxy server for remote databases - apps connect to the proxy instead
- **🔒 Access Control**: Time-based and IP-based access restrictions
- **💉 SQL Injection Detection**: Pattern-based detection blocks attacks automatically
- **🍯 Honeypot Database**: Redirect suspicious queries to fake data
- **📈 Real-time Dashboard**: GUI with live statistics, query history, and security logs
- **📝 Complete Audit Trail**: Every query logged with timestamp, execution time, and decision
- **⚡ Framework Integration**: Works seamlessly with FastAPI, Django, Flask - they don't know the firewall exists!
- **🚨 Alert System**: Email and SMS notifications for security incidents
- **🔍 Threat Analysis**: IP tracking and threat level assessment

## Project Structure

```
src/
├── main.py                      # Application entry point
├── config/
│   ├── settings.py             # Application settings
│   └── database_config.py      # Access control configuration
├── core/
│   ├── firewall.py             # Main firewall logic
│   ├── access_control.py       # Access control rules
│   ├── honeypot.py             # Honeypot database handler
│   └── logger.py               # Security event logger
├── database/
│   ├── db_manager.py           # Database operations manager
│   ├── query_validator.py      # Query validation and sanitization
│   └── fake_data_generator.py  # Generate fake data for honeypot
├── security/
│   ├── injection_detector.py   # SQL/NoSQL injection detection
│   ├── threat_analyzer.py      # Threat level analysis
│   └── ip_tracker.py           # IP address tracking
├── alerts/
│   ├── alert_manager.py        # Alert coordination
│   ├── email_notifier.py       # Email notifications
│   └── sms_notifier.py         # SMS notifications
├── gui/
│   ├── main_window.py          # Main application window
│   ├── dashboard.py            # Statistics dashboard
│   └── log_viewer.py           # Security logs viewer
└── api/
    ├── rest_api.py             # Flask REST API
    └── middleware.py           # API security middleware
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mine
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start - Transparent Firewall

**See [TRANSPARENT_FIREWALL_GUIDE.md](TRANSPARENT_FIREWALL_GUIDE.md) for complete documentation!**

### 1. Simple Example (SQLite)

```python
from database_protection.secure_db_wrapper import initialize_secure_database

# Initialize firewall
secure_db = initialize_secure_database()

# Use it like normal sqlite3 - but with automatic protection!
conn = secure_db.connect('myapp.db', app_id='my_app', ip_address='127.0.0.1')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")  # Automatically intercepted and checked!
results = cursor.fetchall()
conn.close()
```

### 2. FastAPI Integration

```python
from fastapi import FastAPI, Request
from database_protection.secure_db_wrapper import initialize_secure_database

app = FastAPI()
secure_db = initialize_secure_database()

def get_db(request: Request):
    return secure_db.connect('app.db', app_id='fastapi_app', 
                             ip_address=request.client.host)

@app.get("/users")
async def get_users(request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")  # Protected!
    return {"users": cursor.fetchall()}
```

### 3. Launch the GUI Dashboard

```bash
python src/gui/enhanced_main_window.py
```

Then:
- Go to **📊 Query Data** tab to see ALL intercepted queries in real-time!
- Filter by allowed/blocked
- View execution times
- Export audit logs

### 4. Run Database Proxy (for PostgreSQL/MySQL)

```bash
# Start proxy on port 5433, forwarding to PostgreSQL on 5432
python -m src.database_protection.proxy_server --db-type=postgresql

# Now connect your app to localhost:5433 instead of 5432
# ALL queries are intercepted transparently!
```

---

## Usage

### GUI Application

Run the main application with GUI:
```bash
python src/main.py
```

### REST API

Run the Flask API server:
```bash
python -m flask --app src/api/rest_api run
```

API endpoints:
- `POST /api/query` - Execute a database query
- `GET /api/logs` - Retrieve security logs

### Testing the System

Example authorized query:
```python
App ID: admin_panel
IP: 192.168.1.100
Operation: SELECT
Query: SELECT * FROM users
```

Example unauthorized query (will be redirected to honeypot):
```python
App ID: unknown_app
IP: 10.0.0.99
Operation: SELECT
Query: SELECT * FROM users WHERE id=1 OR 1=1
```

## Configuration

### Access Control

Edit `src/config/database_config.py` to configure:
- Authorized applications
- Time windows for access
- IP whitelists
- Allowed operations per application

### Security Settings

Edit `src/config/settings.py` to configure:
- Database paths
- Alert thresholds
- Email/SMS settings
- API settings

## Docker

Build and run with Docker:
```bash
docker build -t db-security-system .
docker run -p 5000:5000 db-security-system
```

## Security Features

### 1. Access Control
- Application-based authentication
- Time-window restrictions
- IP whitelist/blacklist
- Operation-level permissions

### 2. Injection Detection
- SQL injection pattern matching
- NoSQL injection detection
- Query validation
- Dangerous keyword blocking

### 3. Honeypot
- Fake database with realistic data
- Transparent redirection
- Attack pattern collection
- Zero impact on real data

### 4. Monitoring & Alerts
- Real-time dashboard
- Security event logging
- Email/SMS notifications
- Threat level assessment

## Development

### Adding New Detection Patterns

Edit `src/security/injection_detector.py`:
```python
SQL_INJECTION_PATTERNS = [
    r"your_pattern_here",
    # ... existing patterns
]
```

### Customizing Alert Behavior

Edit `src/alerts/alert_manager.py` to customize alert formatting and delivery.

## License

This project is for educational and demonstration purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
