"""
Initialize SQLite3 database for the shop
"""
import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), 'shop.db')

def init_database():
    """Create and populate the shop database"""
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed existing database")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Insert sample users
    users = [
        ('alice', 'alice@shop.com', hashlib.sha256('pass123'.encode()).hexdigest(), 'customer', 1500.00),
        ('bob', 'bob@shop.com', hashlib.sha256('secure456'.encode()).hexdigest(), 'customer', 2300.50),
        ('admin', 'admin@shop.com', hashlib.sha256('admin789'.encode()).hexdigest(), 'admin', 10000.00),
        ('charlie', 'charlie@shop.com', hashlib.sha256('mypass'.encode()).hexdigest(), 'customer', 500.75),
        ('dave', 'dave@shop.com', hashlib.sha256('password'.encode()).hexdigest(), 'moderator', 3200.00),
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, email, password_hash, role, balance)
        VALUES (?, ?, ?, ?, ?)
    ''', users)
    
    # Insert sample products
    products = [
        ('Laptop Pro 15', 1299.99, 15, 'Electronics'),
        ('Wireless Mouse', 29.99, 50, 'Electronics'),
        ('Mechanical Keyboard', 89.99, 30, 'Electronics'),
        ('USB-C Cable', 12.99, 100, 'Accessories'),
        ('Laptop Bag', 49.99, 25, 'Accessories'),
        ('External SSD 1TB', 149.99, 20, 'Storage'),
        ('Webcam HD', 79.99, 35, 'Electronics'),
        ('Desk Lamp LED', 34.99, 40, 'Office'),
        ('Office Chair', 199.99, 10, 'Furniture'),
        ('Standing Desk', 399.99, 5, 'Furniture'),
    ]
    
    cursor.executemany('''
        INSERT INTO products (name, price, stock, category)
        VALUES (?, ?, ?, ?)
    ''', products)
    
    # Insert sample orders
    orders = [
        (1, 1, 1, 1299.99),
        (2, 2, 1, 29.99),
        (1, 3, 2, 179.98),
        (3, 4, 5, 64.95),
    ]
    
    cursor.executemany('''
        INSERT INTO orders (user_id, product_id, quantity, total_price)
        VALUES (?, ?, ?, ?)
    ''', orders)
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM orders')
    order_count = cursor.fetchone()[0]
    
    print(f"\n✅ Database initialized: {DB_PATH}")
    print(f"✅ Created {user_count} users")
    print(f"✅ Created {product_count} products")
    print(f"✅ Created {order_count} orders")
    
    # Display users
    cursor.execute('SELECT id, username, email, role, balance FROM users')
    print("\n👥 Users in database:")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]:12} | {row[2]:20} | {row[3]:10} | ${row[4]:,.2f}")
    
    # Display products
    cursor.execute('SELECT id, name, price, stock, category FROM products LIMIT 5')
    print("\n📦 Sample products:")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]:25} | ${row[2]:7.2f} | Stock: {row[3]:3} | {row[4]}")
    
    conn.close()
    print("\n🚀 Database ready! Start the API with: python app.py")


if __name__ == '__main__':
    init_database()
