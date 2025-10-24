"""
Initialize the demo database with sample data
"""
import sqlite3
import os


def init_database():
    """Create and populate the demo database"""
    db_path = os.path.join(os.path.dirname(__file__), 'demo_db.sqlite3')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample users
    users = [
        ('john_doe', 'john@example.com', 'user', 'hashed_password_1'),
        ('jane_smith', 'jane@example.com', 'user', 'hashed_password_2'),
        ('admin', 'admin@example.com', 'admin', 'hashed_password_admin'),
        ('bob_wilson', 'bob@example.com', 'user', 'hashed_password_3'),
        ('alice_johnson', 'alice@example.com', 'moderator', 'hashed_password_4'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, email, role, password_hash)
        VALUES (?, ?, ?, ?)
    ''', users)
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    
    print(f"✅ Database initialized: {db_path}")
    print(f"✅ Created {count} users")
    
    # Display users
    cursor.execute('SELECT id, username, email, role FROM users')
    print("\n📋 Users in database:")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Role: {row[3]}")
    
    conn.close()


if __name__ == '__main__':
    init_database()
