#!/usr/bin/env python
"""
Database Security System - Main Entry Point
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_gui(firewall=None):
    """Run the GUI application"""
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.enhanced_main_window import EnhancedMainWindow
        
        app = QApplication(sys.argv)
        
        # Create firewall instance if not provided
        if firewall is None:
            from core.firewall import DatabaseFirewall
            firewall = DatabaseFirewall()
        
        # Create and show main window
        main_win = EnhancedMainWindow()
        main_win.firewall = firewall  # Set firewall as attribute
        main_win.show()
        
        sys.exit(app.exec())
    except ImportError as e:
        print(f"Error: {e}")
        print("PyQt6 is required for GUI mode.")
        print("Install it with: pip install PyQt6")
        sys.exit(1)

def run_api():
    """Run the REST API server"""
    from api.rest_api import app
    print("Starting API server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

def run_demo():
    """Run demonstration scenarios"""
    from core.firewall import DatabaseFirewall
    from datetime import datetime, time
    
    print("=== Database Security System Demo ===\n")
    
    # Initialize firewall
    firewall = DatabaseFirewall()
    
    # Test 1: Authorized access
    print("Test 1: Authorized SELECT query")
    is_auth, results, reason = firewall.execute_query(
        app_id='demo_app',
        ip_address='127.0.0.1',
        operation='SELECT',
        query='SELECT * FROM users'
    )
    print(f"Authorized: {is_auth}")
    print(f"Reason: {reason}")
    print(f"Results: {results}\n")
    
    # Test 2: SQL Injection attempt
    print("Test 2: SQL Injection attempt")
    is_auth, results, reason = firewall.execute_query(
        app_id='demo_app',
        ip_address='192.168.1.50',
        operation='SELECT',
        query="SELECT * FROM users WHERE username='admin' OR '1'='1'"
    )
    print(f"Authorized: {is_auth}")
    print(f"Reason: {reason}")
    print(f"Results (honeypot): {results}\n")
    
    # Test 3: Unauthorized IP
    print("Test 3: Unauthorized IP address")
    is_auth, results, reason = firewall.execute_query(
        app_id='webapp_frontend',
        ip_address='10.0.0.100',
        operation='SELECT',
        query='SELECT * FROM users'
    )
    print(f"Authorized: {is_auth}")
    print(f"Reason: {reason}")
    print(f"Results (honeypot): {results}\n")
    
    # Test 4: View security logs
    print("Security Logs:")
    logs = firewall.get_logs()
    for log in logs:
        print(f"  - {log['timestamp']}: {log['app_id']} from {log['ip_address']}")
        print(f"    Reason: {log['reason']}\n")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py [gui|api|demo]")
        print("  gui  - Launch GUI application")
        print("  api  - Start REST API server")
        print("  demo - Run demonstration")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == 'gui':
        from core.firewall import DatabaseFirewall
        firewall_instance = DatabaseFirewall()
        run_gui(firewall_instance)
    elif mode == 'api':
        run_api()
    elif mode == 'demo':
        run_demo()
    else:
        print(f"Unknown mode: {mode}")
        print("Use: gui, api, or demo")
        sys.exit(1)

if __name__ == '__main__':
    main()