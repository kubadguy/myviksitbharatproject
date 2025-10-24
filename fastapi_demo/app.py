"""FastAPI Demo Application"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from database_protection.secure_db_wrapper import initialize_secure_database

app = FastAPI(title="Shop API")

DB_PATH = os.path.join(os.path.dirname(__file__), 'shop.db')
SECURITY_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'security.db')
secure_db = initialize_secure_database(SECURITY_DB_PATH)

def get_db(request: Request = None):
    ip_address = request.client.host if request else "127.0.0.1"
    conn = secure_db.connect(DB_PATH, app_id="shop_api", ip_address=ip_address)
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    return conn

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<html><body><h1>Shop API</h1><p>Endpoints: /products, /users, /search</p></body></html>"

@app.get("/products")
async def get_products(request: Request):
    conn = get_db(request)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock, category FROM products")
    products = cursor.fetchall()
    conn.close()
    return {"success": True, "products": products}

@app.get("/users")
async def get_users(request: Request):
    try:
        conn = get_db(request)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        conn.close()
        return {"success": True, "users": users}
    except Exception as e:
        return JSONResponse(status_code=403, content={"success": False, "error": str(e)})

@app.get("/search")
async def search(q: str, request: Request):
    try:
        conn = get_db(request)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, username, email FROM users WHERE username LIKE '%{q}%'")
        results = cursor.fetchall()
        conn.close()
        return {"success": True, "results": results}
    except Exception as e:
        return JSONResponse(status_code=403, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("Starting Shop API...")
    print("Server: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
