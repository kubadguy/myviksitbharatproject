# Database Security System - Integration Guide

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install database drivers
pip install psycopg2-binary      # PostgreSQL
pip install mysql-connector-python  # MySQL
pip install pymongo              # MongoDB
```

### Run the GUI Application

```bash
python src/main.py
```

##  📊 Multi-Database Support

### SQLite (Built-in)
```python
from database.adapters import SQLiteAdapter

adapter = SQLiteAdapter({'database': '/path/to/db.sqlite'})
adapter.connect()
results = adapter.execute_query("SELECT * FROM users")
```

### PostgreSQL
```python
from database.adapters import PostgreSQLAdapter

adapter = PostgreSQLAdapter({
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb',
    'user': 'postgres',
    'password': 'secret'
})
adapter.connect()
```

### MySQL
```python
from database.adapters import MySQLAdapter

adapter = MySQLAdapter({
    'host': 'localhost',
    'port': 3306,
    'database': 'mydb',
    'user': 'root',
    'password': 'secret'
})
adapter.connect()
```

### MongoDB
```python
from database.adapters import MongoDBAdapter

adapter = MongoDBAdapter({
    'host': 'localhost',
    'port': 27017,
    'database': 'mydb',
    'user': 'admin',  # optional
    'password': 'secret'  # optional
})
adapter.connect()
```

## 🔌 Framework Integration

### Flask Integration

```python
from flask import Flask
from framework_adapters import FlaskSecurityAdapter

app = Flask(__name__)
security = FlaskSecurityAdapter(app)

# Create security monitoring routes
security.create_routes(app)

@app.route('/api/users')
@security.protect(app_id='my_app', operation='SELECT')
def get_users():
    is_auth, results, reason = security.execute("SELECT * FROM users")
    
    if is_auth:
        return {'users': results}, 200
    else:
        return {'error': reason}, 403

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Available Routes:**
- `GET /api/security/logs` - Get security logs
- `GET /api/security/stats` - Get security statistics
- `POST /api/security/query` - Execute protected query

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, Request
from framework_adapters import FastAPISecurityMiddleware

app = FastAPI()
security = FastAPISecurityMiddleware()

# Create security routes
security.create_routes(app)

@app.get("/api/users")
async def get_users(
    request: Request,
    auth=Depends(security.protect(app_id="my_app", operation="SELECT"))
):
    results = await security.execute(request, "SELECT * FROM users")
    return {'users': results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run with:**
```bash
uvicorn app:app --reload
```

### Django Integration

**1. Add to `settings.py`:**

```python
MIDDLEWARE = [
    ...
    'framework_adapters.django_adapter.DjangoSecurityMiddleware',
]

DB_SECURITY_CONFIG = {
    'enabled': True,
    'app_id': 'django_app',
}
```

**2. Use in views:**

```python
from django.http import JsonResponse
from framework_adapters.django_adapter import protect_query

@protect_query(app_id='webapp_frontend', operation='SELECT')
def get_users(request):
    is_auth, results, reason = request.db_security.execute_query(
        request,
        app_id=request.security_app_id,
        operation=request.security_operation,
        query='SELECT * FROM users'
    )
    
    if is_auth:
        return JsonResponse({'users': results})
    else:
        return JsonResponse({'error': reason}, status=403)
```

**3. Django REST Framework:**

```python
from rest_framework import viewsets
from rest_framework.response import Response
from framework_adapters.django_adapter import DRFSecurityMixin

class UserViewSet(DRFSecurityMixin, viewsets.ModelViewSet):
    security_app_id = 'api'
    security_operation = 'SELECT'
    
    def list(self, request):
        is_auth, results, reason = self.execute_secure_query(
            'SELECT * FROM users'
        )
        return Response({'users': results})
```

## 🌐 Cross-Language Integration

### Express.js (Node.js)

Create a proxy service:

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const SECURITY_API = 'http://localhost:5000/api/security';

app.post('/api/query', async (req, res) => {
    try {
        const response = await axios.post(`${SECURITY_API}/query`, {
            app_id: 'express_app',
            operation: 'SELECT',
            query: req.body.query
        });
        
        res.json(response.data);
    } catch (error) {
        res.status(403).json({ error: error.response.data });
    }
});

app.listen(3000);
```

### Laravel (PHP)

```php
<?php
// app/Services/DatabaseSecurity.php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class DatabaseSecurity
{
    private $securityApi = 'http://localhost:5000/api/security';
    
    public function executeQuery($appId, $operation, $query)
    {
        $response = Http::post("{$this->securityApi}/query", [
            'app_id' => $appId,
            'operation' => $operation,
            'query' => $query
        ]);
        
        if ($response->successful()) {
            return $response->json();
        }
        
        throw new \Exception('Security check failed');
    }
}

// Usage in controller
public function getUsers(DatabaseSecurity $security)
{
    $result = $security->executeQuery(
        'laravel_app',
        'SELECT',
        'SELECT * FROM users'
    );
    
    return response()->json($result);
}
```

## ⚙️ Configuration

### Access Control Rules

Edit `src/config/database_config.py`:

```python
AUTHORIZED_APPS = {
    'my_app': {
        'time_windows': [(9, 17)],  # 9 AM - 5 PM
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE'],
        'ip_whitelist': ['192.168.1.0/24', '10.0.0.5']
    },
    'admin_panel': {
        'time_windows': [(0, 23)],  # 24/7
        'allowed_operations': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
        'ip_whitelist': ['192.168.1.100']
    },
}
```

### Security Settings

Edit `src/config/settings.py`:

```python
class Settings:
    # Database settings
    REAL_DB_PATH = os.path.join(BASE_DIR, 'data', 'real_database.db')
    HONEYPOT_DB_PATH = os.path.join(BASE_DIR, 'data', 'honeypot_database.db')
    
    # Security settings
    MAX_FAILED_ATTEMPTS = 3
    ALERT_THRESHOLD = 5
    
    # Alert settings
    ENABLE_EMAIL_ALERTS = True
    ENABLE_SMS_ALERTS = False
    ADMIN_EMAIL = "admin@company.com"
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    API_DEBUG = False
```

## 📱 GUI Features

### Database Configuration
1. Click "⚙️ Database Config"
2. Select database type (SQLite, PostgreSQL, MySQL, MongoDB)
3. Enter connection details
4. Click "Test Connection"
5. Click "OK" to save

### Query Testing
1. Go to "🔍 Query Testing" tab
2. Enter App ID, IP Address
3. Select operation (SELECT, INSERT, UPDATE, DELETE)
4. Enter SQL query
5. Click "🚀 Execute Query"

### Security Dashboard
- View real-time statistics
- Monitor total/blocked queries
- Track unique IPs
- See recent activity

### Security Logs
- Filter by App ID, IP, or Reason
- Color-coded threat levels
- Export logs to JSON
- Clear logs

## 🔒 Security Features

### SQL Injection Detection
Automatically detects patterns like:
- `OR 1=1`
- `UNION SELECT`
- `'; DROP TABLE`
- Comment-based attacks

### Time-Based Access Control
- Configure specific time windows
- Automatic blocking outside hours
- Timezone support

### IP Whitelisting
- CIDR notation support
- Multiple IP ranges
- Dynamic IP management

### Honeypot System
- Transparent redirection
- Realistic fake data
- Attack pattern collection
- Zero risk to real data

## 📊 Monitoring & Alerts

### Email Alerts
Configure SMTP in `alerts/email_notifier.py`:

```python
notifier = EmailNotifier(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    sender_email='alert@company.com',
    sender_password='your_password'
)
```

### SMS Alerts
Integrate with Twilio:

```python
from alerts.sms_notifier import SMSNotifier

notifier = SMSNotifier(
    api_key='your_twilio_key',
    api_url='https://api.twilio.com/...'
)
```

## 🧪 Testing

Run the test suite:

```bash
python test_system.py
```

## 🐳 Docker Deployment

```bash
docker build -t db-security-system .
docker run -p 5000:5000 -p 8000:8000 db-security-system
```

## 📚 API Reference

### REST API Endpoints

#### Execute Protected Query
```http
POST /api/security/query
Content-Type: application/json

{
    "app_id": "my_app",
    "operation": "SELECT",
    "query": "SELECT * FROM users WHERE id = 1"
}
```

**Response:**
```json
{
    "authorized": true,
    "results": [...],
    "reason": "Access granted"
}
```

#### Get Security Logs
```http
GET /api/security/logs
```

**Response:**
```json
{
    "logs": [
        {
            "app_id": "unknown_app",
            "ip_address": "1.2.3.4",
            "operation": "SELECT",
            "reason": "Unknown application",
            "query": "SELECT * FROM users",
            "action": "REDIRECTED_TO_HONEYPOT"
        }
    ]
}
```

#### Get Security Statistics
```http
GET /api/security/stats
```

**Response:**
```json
{
    "total_queries": 150,
    "blocked_queries": 23,
    "unique_ips": 45
}
```

## 🛠️ Troubleshooting

### Database Connection Issues

**PostgreSQL:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d mydb
```

**MySQL:**
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Test connection
mysql -h localhost -u root -p
```

**MongoDB:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Test connection
mongo --host localhost --port 27017
```

### Import Errors

If you get import errors, ensure all dependencies are installed:

```bash
pip install --upgrade -r requirements.txt
```

### GUI Issues

If GUI doesn't start, check PyQt6 installation:

```bash
pip uninstall PyQt6
pip install PyQt6==6.6.0
```

## 📖 Additional Resources

- [Security Best Practices](./docs/security.md)
- [Performance Tuning](./docs/performance.md)
- [API Documentation](./docs/api.md)
- [Contributing Guide](./CONTRIBUTING.md)

## 💡 Examples

See the `examples/` directory for:
- Flask app integration
- FastAPI microservice
- Django project setup
- Express.js proxy
- Laravel middleware

## 🤝 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/...)
- Documentation: [Read the docs](https://docs...)
- Email: support@...

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.
