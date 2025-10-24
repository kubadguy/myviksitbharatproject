"""
"""FastAPI Demo Application - Clean Shop API
Real-world API with SQLite3 database
The security is transparent - this app has NO knowledge of the protection system!
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

# Import the transparent secure database wrapper
from database_protection.secure_db_wrapper import initialize_secure_database

# Initialize FastAPI app
app = FastAPI(
    title="Shop API",
    description="E-commerce API"
)

# Database paths
DB_PATH = os.path.join(os.path.dirname(__file__), 'shop.db')
SECURITY_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'security.db')

# Initialize the transparent security wrapper
secure_db = initialize_secure_database(SECURITY_DB_PATH)


# Pydantic models
class User(BaseModel):
    username: str
    email: str
    role: str


class Product(BaseModel):
    name: str
    price: float
    stock: int


def get_db(request: Request = None):
    """Get database connection - transparently secured!"""
    ip_address = request.client.host if request else "127.0.0.1"
    
    # This looks like a normal sqlite3.connect() but it's protected!
    # The app doesn't know about security - it's transparent
    conn = secure_db.connect(
        DB_PATH,
        app_id="shop_api",
        ip_address=ip_address
    )
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    return conn


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with API documentation"""
    html = '''
    <html>
    <head>
        <title>Shop API</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }
            code { background: #34495e; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Shop API</h1>
            <p>E-commerce API with transparent security protection</p>
            
            <h2>Endpoints</h2>
            <div class="endpoint"><b>GET /products</b> - List all products</div>
            <div class="endpoint"><b>GET /product/{id}</b> - Get product details</div>
            <div class="endpoint"><b>GET /users</b> - List all users</div>
            <div class="endpoint"><b>GET /user/{id}</b> - Get user by ID</div>
            <div class="endpoint"><b>GET /search?q=...</b> - Search users (vulnerable!)</div>
            <div class="endpoint"><b>GET /admin/stats</b> - Statistics</div>
            
            <h2>Test It</h2>
            <p><b>Normal user:</b> <code>python customer.py</code></p>
            <p><b>Hacker:</b> <code>python hacker.py</code></p>
        </div>
    </body>
    </html>
    '''
    return html


@app.get("/products")
async def get_products(request: Request):
    """Get all products - Public endpoint"""
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock, category FROM products")
    products = cursor.fetchall()
    conn.close()
    
    return {
        "success": True,
        "products": products,
        "count": len(products)
    }


@app.get("/product/{product_id}")
async def get_product(product_id: int, request: Request):
    """Get product by ID - Public endpoint"""
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if product:
        return {"success": True, "product": product}
    else:
        raise HTTPException(status_code=404, detail="Product not found")


@app.get("/users")
async def get_users(request: Request):
    """Get all users - App does not know it is protected"""
    try:
        conn = get_db(request)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at FROM users")
        users = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        # If security blocks it, we get an exception
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": str(e),
                "message": "Access denied"
            }
        )


@app.get("/user/{user_id}")
async def get_user(user_id: int, request: Request):
    """Get user by ID - App has no idea about security"""
    try:
        conn = get_db(request)
        cursor = conn.cursor()
        # Intentionally vulnerable - using f-string instead of parameterized query
        cursor.execute(f"SELECT id, username, email, role FROM users WHERE id = {user_id}")
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"success": True, "user": user}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": str(e)}
        )


@app.get("/search")
async def search(q: str, request: Request):
    """Search endpoint - INTENTIONALLY VULNERABLE to SQL injection.
    The app does not know about security - protection is transparent.
    """
    try:
        conn = get_db(request)
        cursor = conn.cursor()
        # VULNERABLE: Direct string interpolation - security wrapper will catch attacks
        cursor.execute(f"SELECT id, username, email FROM users WHERE username LIKE '%{q}%' OR email LIKE '%{q}%'")
        results = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "results": results,
            "search_term": q
        }
    except Exception as e:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": str(e),
                "message": f"Query blocked: {q}"
            }
        )


@app.get("/admin/stats")
async def admin_stats(request: Request):
    """Admin statistics endpoint"""
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()['COUNT(*)']
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()['COUNT(*)']
    conn.close()
    
    return {
        "database": {
            "users": user_count,
            "products": product_count
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Shop API...")
    print("📍 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🛡️  Security: Transparent (app has no knowledge of protection)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
