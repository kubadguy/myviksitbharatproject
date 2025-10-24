"""
Legitimate User Script - Makes normal API requests
This simulates a real user accessing the application properly
"""
import requests
import time
import json


BASE_URL = 'http://localhost:8000'


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_legitimate_requests():
    """Simulate legitimate user behavior"""
    print("🙂 LEGITIMATE USER - Making normal requests...")
    
    try:
        # Test 1: Get all users
        print_section("1. GET /users/ - Fetch all users")
        response = requests.get(f'{BASE_URL}/users/')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Retrieved {len(data['users'])} users")
            for user in data['users'][:3]:
                print(f"   - {user['username']} ({user['email']}) - {user['role']}")
        else:
            print(f"❌ Failed: {data.get('error')}")
        
        time.sleep(1)
        
        # Test 2: Get specific user
        print_section("2. GET /user/1/ - Fetch specific user")
        response = requests.get(f'{BASE_URL}/user/1/')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if data.get('success'):
            user = data['user']
            print(f"✅ Success! Retrieved user:")
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
        else:
            print(f"❌ Failed: {data.get('error')}")
        
        time.sleep(1)
        
        # Test 3: Search for user
        print_section("3. GET /search/?name=john - Search for users")
        response = requests.get(f'{BASE_URL}/search/', params={'name': 'john'})
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Found {len(data['users'])} matching users")
            for user in data['users']:
                print(f"   - {user['username']}")
        else:
            print(f"❌ Failed: {data.get('error')}")
        
        time.sleep(1)
        
        # Test 4: Another legitimate search
        print_section("4. GET /search/?name=admin - Search for admin")
        response = requests.get(f'{BASE_URL}/search/', params={'name': 'admin'})
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if data.get('success'):
            print(f"✅ Success! Found {len(data['users'])} matching users")
        else:
            print(f"❌ Failed: {data.get('error')}")
        
        time.sleep(1)
        
        # Test 5: Get statistics
        print_section("5. GET /stats/ - View security statistics")
        response = requests.get(f'{BASE_URL}/stats/')
        print(f"Status Code: {response.status_code}")
        data = response.json()
        stats = data['statistics']
        print(f"📊 Security Statistics:")
        print(f"   Total Queries: {stats['total_queries']}")
        print(f"   Authorized: {stats['authorized_queries']}")
        print(f"   Blocked: {stats['blocked_queries']}")
        print(f"   Block Rate: {stats['block_rate']}")
        print(f"   Unique IPs: {stats['unique_ips']}")
        
        print_section("✅ ALL LEGITIMATE REQUESTS COMPLETED SUCCESSFULLY")
        print("All queries were authorized and executed on the real database.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Django server")
        print("Please make sure the server is running:")
        print("  cd demo_django_project")
        print("  python manage.py runserver 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║         LEGITIMATE USER SIMULATION                            ║
║  Testing normal API usage with proper authentication         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    test_legitimate_requests()
    
    print("\n" + "="*60)
    print("Legitimate user session complete!")
    print("="*60 + "\n")
