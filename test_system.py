#!/usr/bin/env python3
"""
Test script for Database Security System
Run this to verify the system is working correctly
"""

import sys
sys.path.insert(0, 'src')

from core.firewall import DatabaseFirewall
from datetime import datetime

def test_authorized_access():
    """Test authorized database access"""
    print("\n" + "="*60)
    print("TEST 1: Authorized Access")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    # Simulate authorized access during business hours (9 AM - 5 PM)
    test_time = datetime(2024, 1, 1, 10, 0)  # 10 AM
    
    is_auth, results, reason = firewall.execute_query(
        app_id='admin_panel',
        ip_address='192.168.1.100',
        operation='SELECT',
        query='SELECT * FROM users',
        simulate_time=test_time
    )
    
    print(f"✓ Status: {'AUTHORIZED' if is_auth else 'BLOCKED'}")
    print(f"✓ Reason: {reason}")
    print(f"✓ Results: {results}")
    
    return is_auth


def test_sql_injection():
    """Test SQL injection detection"""
    print("\n" + "="*60)
    print("TEST 2: SQL Injection Detection")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    # Attempt SQL injection
    is_auth, results, reason = firewall.execute_query(
        app_id='admin_panel',
        ip_address='192.168.1.100',
        operation='SELECT',
        query="SELECT * FROM users WHERE id=1 OR '1'='1'",
        simulate_time=datetime(2024, 1, 1, 10, 0)
    )
    
    print(f"✓ Status: {'AUTHORIZED' if is_auth else 'BLOCKED (Expected)'}")
    print(f"✓ Reason: {reason}")
    print(f"✓ Honeypot returned {len(results)} fake records")
    
    return not is_auth  # Should be blocked


def test_unauthorized_ip():
    """Test unauthorized IP address"""
    print("\n" + "="*60)
    print("TEST 3: Unauthorized IP Address")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    is_auth, results, reason = firewall.execute_query(
        app_id='admin_panel',
        ip_address='10.0.0.99',  # Not in whitelist
        operation='SELECT',
        query='SELECT * FROM users',
        simulate_time=datetime(2024, 1, 1, 10, 0)
    )
    
    print(f"✓ Status: {'AUTHORIZED' if is_auth else 'BLOCKED (Expected)'}")
    print(f"✓ Reason: {reason}")
    print(f"✓ Honeypot returned {len(results)} fake records")
    
    return not is_auth  # Should be blocked


def test_time_window():
    """Test time window restrictions"""
    print("\n" + "="*60)
    print("TEST 4: Time Window Restriction")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    # Simulate access outside business hours (2 AM)
    test_time = datetime(2024, 1, 1, 2, 0)
    
    is_auth, results, reason = firewall.execute_query(
        app_id='webapp_frontend',  # Only allowed 9 AM - 5 PM
        ip_address='192.168.1.50',
        operation='SELECT',
        query='SELECT * FROM users',
        simulate_time=test_time
    )
    
    print(f"✓ Status: {'AUTHORIZED' if is_auth else 'BLOCKED (Expected)'}")
    print(f"✓ Reason: {reason}")
    
    return not is_auth  # Should be blocked


def test_unauthorized_operation():
    """Test unauthorized operation"""
    print("\n" + "="*60)
    print("TEST 5: Unauthorized Operation")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    is_auth, results, reason = firewall.execute_query(
        app_id='backup_service',  # Only allowed SELECT
        ip_address='10.0.0.5',
        operation='DELETE',
        query='DELETE FROM users WHERE id=1',
        simulate_time=datetime(2024, 1, 1, 3, 0)
    )
    
    print(f"✓ Status: {'AUTHORIZED' if is_auth else 'BLOCKED (Expected)'}")
    print(f"✓ Reason: {reason}")
    
    return not is_auth  # Should be blocked


def test_logging():
    """Test security logging"""
    print("\n" + "="*60)
    print("TEST 6: Security Logging")
    print("="*60)
    
    firewall = DatabaseFirewall()
    
    # Generate some log entries
    firewall.execute_query(
        'unknown_app', '1.2.3.4', 'SELECT', 
        'SELECT * FROM users', datetime.now()
    )
    
    logs = firewall.get_logs()
    print(f"✓ Total log entries: {len(logs)}")
    
    if logs:
        print(f"✓ Sample log entry:")
        print(f"  - App: {logs[0]['app_id']}")
        print(f"  - IP: {logs[0]['ip_address']}")
        print(f"  - Reason: {logs[0]['reason']}")
    
    return len(logs) > 0


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DATABASE SECURITY SYSTEM - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Authorized Access", test_authorized_access),
        ("SQL Injection Detection", test_sql_injection),
        ("Unauthorized IP", test_unauthorized_ip),
        ("Time Window Restriction", test_time_window),
        ("Unauthorized Operation", test_unauthorized_operation),
        ("Security Logging", test_logging),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ ERROR in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! The system is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
