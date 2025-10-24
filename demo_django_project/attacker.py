"""
Attacker Script - Attempts various SQL injection attacks
This demonstrates how the security system blocks malicious queries
"""
import requests
import time


BASE_URL = 'http://localhost:8000'


def print_attack(number, description):
    """Print attack header"""
    print(f"\n{'='*70}")
    print(f"🔴 ATTACK #{number}: {description}")
    print('='*70)


def attempt_attack(endpoint, params=None, description=""):
    """Attempt an attack and show result"""
    print(f"Target: {endpoint}")
    if params:
        print(f"Params: {params}")
    
    try:
        if params:
            response = requests.get(f'{BASE_URL}{endpoint}', params=params)
        else:
            response = requests.get(f'{BASE_URL}{endpoint}')
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 403:
            print(f"🛡️  BLOCKED by Security System!")
            print(f"Reason: {data.get('error', 'Unknown')}")
            print(f"Message: {data.get('message', '')}")
            if 'fake_data' in data:
                print(f"📦 Received HONEYPOT data (not real database)")
                return False
        elif data.get('success'):
            print(f"⚠️  ATTACK SUCCEEDED - Security breach!")
            return True
        else:
            print(f"❓ Unexpected response: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    
    return False


def run_attack_simulation():
    """Run comprehensive attack simulation"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🚨 ATTACKER SIMULATION 🚨                     ║
║  Testing SQL injection and other malicious queries               ║
║  All attacks should be BLOCKED by the security system            ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    attacks_attempted = 0
    attacks_blocked = 0
    attacks_succeeded = 0
    
    try:
        # Attack 1: Classic SQL Injection with OR 1=1
        print_attack(1, "Classic SQL Injection - OR 1=1")
        result = attempt_attack('/search/', {'name': "' OR '1'='1"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 2: UNION-based SQL Injection
        print_attack(2, "UNION-based SQL Injection")
        result = attempt_attack('/search/', {'name': "' UNION SELECT id, username, email, password_hash FROM users--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 3: Comment-based bypass
        print_attack(3, "Comment-based Bypass Attack")
        result = attempt_attack('/search/', {'name': "admin'--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 4: Boolean-based blind SQL injection
        print_attack(4, "Boolean-based Blind SQLi")
        result = attempt_attack('/search/', {'name': "' AND 1=1--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 5: Stacked queries attempt
        print_attack(5, "Stacked Queries Attack")
        result = attempt_attack('/search/', {'name': "'; DROP TABLE users;--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 6: Time-based blind SQL injection
        print_attack(6, "Time-based Blind SQLi")
        result = attempt_attack('/search/', {'name': "' OR SLEEP(5)--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 7: Error-based SQL injection
        print_attack(7, "Error-based SQLi")
        result = attempt_attack('/search/', {'name': "' AND (SELECT * FROM users)--"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 8: Double encoding attack
        print_attack(8, "Double Encoding Attack")
        result = attempt_attack('/search/', {'name': "%2527%20OR%20%25271%2527=%25271"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 9: NULL byte injection
        print_attack(9, "NULL Byte Injection")
        result = attempt_attack('/search/', {'name': "admin%00"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Attack 10: Hex encoding attack
        print_attack(10, "Hex Encoding Attack")
        result = attempt_attack('/search/', {'name': "0x61646d696e"})
        attacks_attempted += 1
        if result == False:
            attacks_blocked += 1
        elif result == True:
            attacks_succeeded += 1
        time.sleep(1)
        
        # Display attack summary
        print("\n" + "="*70)
        print("📊 ATTACK SIMULATION SUMMARY")
        print("="*70)
        print(f"Total Attacks Attempted: {attacks_attempted}")
        print(f"🛡️  Attacks Blocked: {attacks_blocked}")
        print(f"⚠️  Attacks Succeeded: {attacks_succeeded}")
        print(f"🎯 Block Rate: {(attacks_blocked/attacks_attempted*100):.1f}%")
        print("="*70)
        
        if attacks_succeeded == 0:
            print("\n✅ SUCCESS! All attacks were blocked by the security system!")
            print("🛡️  The database is fully protected against SQL injection attacks.")
        else:
            print(f"\n⚠️  WARNING: {attacks_succeeded} attack(s) succeeded!")
            print("Security system may need adjustment.")
        
        # Get final statistics
        print("\n" + "="*70)
        print("📈 Checking Security Statistics...")
        print("="*70)
        try:
            response = requests.get(f'{BASE_URL}/stats/')
            if response.status_code == 200:
                data = response.json()
                stats = data['statistics']
                print(f"Total Queries: {stats['total_queries']}")
                print(f"Blocked Queries: {stats['blocked_queries']}")
                print(f"Block Rate: {stats['block_rate']}")
                
                if data['recent_blocks']:
                    print(f"\nRecent Blocked Attacks:")
                    for block in data['recent_blocks'][-5:]:
                        print(f"  - IP: {block['ip']}")
                        print(f"    Reason: {block['reason']}")
                        print(f"    Query: {block['query'][:80]}...")
                        print()
        except Exception as e:
            print(f"Could not retrieve statistics: {e}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Django server")
        print("Please make sure the server is running:")
        print("  cd demo_django_project")
        print("  python manage.py runserver 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == '__main__':
    run_attack_simulation()
    
    print("\n" + "="*70)
    print("Attack simulation complete!")
    print("="*70 + "\n")
