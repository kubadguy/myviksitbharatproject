import os
import sys
import sqlite3
from typing import Any, Dict
from flask import Flask, request, jsonify

# Add src to path for database guardian
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the secure database guardian
from database_protection.secure_db_guardian import initialize_secure_database

DB_PATH = os.path.join(CURRENT_DIR, 'main.db')
SECURITY_DB_PATH = os.path.join(CURRENT_DIR, 'security_guardian.db')

# Initialize the guardian
guardian = initialize_secure_database(SECURITY_DB_PATH)

# Give test_server permission to initialize database
guardian.set_permissions("test_server", {
    'read': True,
    'write': True, 
    'create': True,  # Allow CREATE TABLE for initialization
    'drop': False,
    'alter': False
})

app = Flask(__name__)


def ensure_db():
    os.makedirs(CURRENT_DIR, exist_ok=True)
    conn = guardian.connect(DB_PATH, app_id="test_server", ip_address="127.0.0.1")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT,
            balance REAL
        )
        """
    )
    # Seed if empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO users (username,email,password,balance) VALUES (?,?,?,?)",
            [
                ("alice", "alice@example.com", "real_hash_a", 1000.0),
                ("bob", "bob@example.com", "real_hash_b", 500.0),
                ("charlie", "charlie@example.com", "real_hash_c", 250.0),
            ],
        )
    conn.commit()
    conn.close()


def query_all(sql: str, params: tuple = ()):  # Helper for SELECTs
    conn = guardian.connect(DB_PATH, app_id="test_server", ip_address="127.0.0.1")
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def execute(sql: str, params: tuple = ()):  # Helper for write operations
    conn = guardian.connect(DB_PATH, app_id="test_server", ip_address="127.0.0.1")
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


@app.get("/users")
def list_users():
    ensure_db()
    rows = query_all("SELECT id, username, email, balance FROM users")
    return jsonify({"ok": True, "rows": rows})


@app.get("/users/search")
def search_users():
    ensure_db()
    q = request.args.get("q", "")
    rows = query_all(
        "SELECT id, username, email, balance FROM users WHERE username LIKE ?",
        (f"%{q}%",),
    )
    return jsonify({"ok": True, "rows": rows})


@app.post("/users")
def add_user():
    ensure_db()
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    username = str(data.get("username", ""))
    email = str(data.get("email", ""))
    password = str(data.get("password", ""))
    try:
        balance = float(data.get("balance", 0))
    except Exception:
        balance = 0.0
    execute(
        "INSERT INTO users (username,email,password,balance) VALUES (?,?,?,?)",
        (username, email, password, balance),
    )
    return jsonify({"ok": True})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    ensure_db()
    app.run(host="127.0.0.1", port=5055, debug=False)
