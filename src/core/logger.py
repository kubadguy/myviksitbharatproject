from datetime import datetime
from typing import List, Dict
import time

class SecurityLogger:
    def __init__(self):
        self.logs = []
        self.query_history = []  # Track ALL queries, not just intrusions

    def log_query(self, app_id: str, ip_address: str, operation: str, 
                  query: str, is_authorized: bool, reason: str, 
                  execution_time_ms: float = 0):
        """Log all database queries (both authorized and blocked)"""
        query_entry = {
            'timestamp': datetime.now().isoformat(),
            'unix_timestamp': time.time(),
            'app_id': app_id,
            'ip_address': ip_address,
            'operation': operation,
            'query': query,
            'is_authorized': is_authorized,
            'reason': reason,
            'status': 'ALLOWED' if is_authorized else 'BLOCKED',
            'execution_time_ms': execution_time_ms
        }
        self.query_history.append(query_entry)
        return query_entry

    def log_intrusion(self, app_id: str, ip_address: str,
                     operation: str, query: str, reason: str):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'app_id': app_id,
            'ip_address': ip_address,
            'operation': operation,
            'query': query,
            'reason': reason,
            'action': 'REDIRECTED_TO_HONEYPOT'
        }
        self.logs.append(log_entry)
        return log_entry

    def get_logs(self, limit: int = None) -> List[Dict]:
        if limit:
            return self.logs[-limit:]
        return self.logs
    
    def get_query_history(self, limit: int = None, filter_status: str = None) -> List[Dict]:
        """Get query history with optional filtering"""
        history = self.query_history
        
        # Filter by status if requested
        if filter_status:
            history = [q for q in history if q['status'] == filter_status]
        
        # Apply limit
        if limit:
            return history[-limit:]
        return history
    
    def get_query_stats(self) -> Dict:
        """Get statistics about queries"""
        total = len(self.query_history)
        allowed = sum(1 for q in self.query_history if q['is_authorized'])
        blocked = total - allowed
        
        return {
            'total_queries': total,
            'allowed': allowed,
            'blocked': blocked,
            'block_rate': (blocked / total * 100) if total > 0 else 0
        }

    def clear_logs(self):
        self.logs = []
    
    def clear_query_history(self):
        self.query_history = []
