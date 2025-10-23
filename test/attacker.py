import os
import sys
import time
import json
import requests

# Make project src importable for any shared constants (optional)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

BASE_URL = "http://127.0.0.1:5055"

TEST_SEARCH_QUERIES = [
    "alice",
    "bob",
    "nonexistent",
    # Suspicious payloads to exercise detection paths; server escapes them
    "' OR '1'='1",
    "abc%25' UNION SELECT 1,2,3,4 --",
    "'; DROP TABLE users; --",
]

NEW_USERS = [
    {"username": "eve", "email": "eve@example.com", "password": "pw1", "balance": 12.5},
    {"username": "mallory", "email": "mallory@example.com", "password": "pw2", "balance": 33.0},
]

def main():
    # Health check
    r = requests.get(f"{BASE_URL}/health")
    print("health:", r.status_code, r.text)

    # List users
    r = requests.get(f"{BASE_URL}/users")
    print("list:", r.status_code, r.json())

    # Add some users
    for u in NEW_USERS:
        r = requests.post(f"{BASE_URL}/users", json=u)
        print("add:", u["username"], r.status_code, r.json())

    # Search with various inputs
    for q in TEST_SEARCH_QUERIES:
        r = requests.get(f"{BASE_URL}/users/search", params={"q": q})
        print("search:", q, r.status_code)
        try:
            print(json.dumps(r.json(), indent=2)[:400])
        except Exception:
            print(r.text[:400])
        time.sleep(0.2)

if __name__ == "__main__":
    main()
