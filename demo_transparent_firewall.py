#!/usr/bin/env python3
"""
Transparent Database Firewall Demo
Shows how queries are intercepted and checked automatically
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_protection.secure_db_wrapper import initialize_secure_database
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def demo_transparent_protection():
    """Demonstrate transparent query interception"""
    
    print_header("🔥 Transparent Database Firewall Demo")
    
    # Initialize the firewall
    print("1️⃣  Initializing secure database wrapper...")
    secure_db = initialize_secure_database()
    print("   ✅ Firewall initialized!\n")
    
    # Create a test database
    print("2️⃣  Creating test database...")
    conn = secure_db.connect(':memory:', app_id='demo_app', ip_address='127.0.0.1')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO users VALUES (1, 'alice', 'alice@example.com', 'hash1')")
    cursor.execute("INSERT INTO users VALUES (2, 'bob', 'bob@example.com', 'hash2')")
    conn.commit()
    print("   ✅ Test database created with sample data\n")
    
    # Demo 1: Legitimate Query
    print_header("✅ Demo 1: Legitimate Query")
    print("Query: SELECT * FROM users WHERE id = 1")
    print("\nExecuting...")
    time.sleep(0.5)
    
    try:
        cursor.execute("SELECT * FROM users WHERE id = 1")
        results = cursor.fetchall()
        print(f"✅ Query ALLOWED!")
        print(f"📊 Results: {results}")
        print("🔍 Firewall checked the query and allowed it to execute")
    except Exception as e:
        print(f"❌ Query BLOCKED: {e}")
    
    # Demo 2: SQL Injection Attempt
    print_header("🚨 Demo 2: SQL Injection Attack")
    print("Query: SELECT * FROM users WHERE username = 'admin' OR 1=1--'")
    print("\nExecuting...")
    time.sleep(0.5)
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = 'admin' OR 1=1--'")
        results = cursor.fetchall()
        print(f"Results: {results}")
    except Exception as e:
        print(f"❌ Query BLOCKED by firewall!")
        print(f"🛡️  Reason: {e}")
        print("🔍 The firewall detected SQL injection pattern and blocked it")
    
    # Demo 3: Union-based Injection
    print_header("🚨 Demo 3: UNION-based SQL Injection")
    print("Query: SELECT * FROM users UNION SELECT 1,2,3,4")
    print("\nExecuting...")
    time.sleep(0.5)
    
    try:
        cursor.execute("SELECT * FROM users UNION SELECT 1,2,3,4")
        results = cursor.fetchall()
        print(f"Results: {results}")
    except Exception as e:
        print(f"❌ Query BLOCKED by firewall!")
        print(f"🛡️  Reason: {e}")
        print("🔍 UNION-based injection detected and blocked")
    
    # Demo 4: Dangerous Operation
    print_header("⚠️  Demo 4: Potentially Dangerous Query")
    print("Query: DELETE FROM users")
    print("\nExecuting...")
    time.sleep(0.5)
    
    try:
        cursor.execute("DELETE FROM users")
        print(f"✅ Query executed (based on access control rules)")
    except Exception as e:
        print(f"❌ Query BLOCKED by firewall!")
        print(f"🛡️  Reason: {e}")
    
    # Show statistics
    print_header("📊 Firewall Statistics")
    stats = secure_db.firewall.logger.get_query_stats()
    print(f"Total Queries:  {stats['total_queries']}")
    print(f"Allowed:        {stats['allowed']} ({100 - stats['block_rate']:.1f}%)")
    print(f"Blocked:        {stats['blocked']} ({stats['block_rate']:.1f}%)")
    
    # Show query history
    print("\n📝 Query History:")
    history = secure_db.firewall.logger.get_query_history(limit=10)
    for i, query in enumerate(history, 1):
        status = "✅" if query['is_authorized'] else "❌"
        print(f"\n{i}. {status} [{query['status']}] {query['operation']}")
        print(f"   Query: {query['query'][:60]}...")
        print(f"   Reason: {query['reason']}")
        print(f"   Time: {query['execution_time_ms']:.2f}ms")
    
    conn.close()
    
    # Final summary
    print_header("🎉 Demo Complete!")
    print("Key Takeaways:")
    print("  ✅ All queries are intercepted transparently")
    print("  ✅ SQL injection attempts are automatically blocked")
    print("  ✅ Complete audit trail is maintained")
    print("  ✅ Applications don't know the firewall exists!")
    print("\n💡 Next Steps:")
    print("  1. Run: python src/gui/enhanced_main_window.py")
    print("  2. Go to 'Query Data' tab to see all queries")
    print("  3. Integrate with your FastAPI/Django/Flask app")
    print("  4. Read TRANSPARENT_FIREWALL_GUIDE.md for details")
    print("\n")


if __name__ == '__main__':
    try:
        demo_transparent_protection()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
