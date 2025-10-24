from typing import Dict, List
from datetime import datetime, timedelta


class ThreatAnalyzer:
    def __init__(self):
        self.threat_history = []
        self.ip_attempts = {}

    def analyze_threat_level(self, ip_address: str, reason: str) -> str:
        """
        Analyze threat level based on attack patterns and frequency
        Returns: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        """
        # Record the attempt
        current_time = datetime.now()
        if ip_address not in self.ip_attempts:
            self.ip_attempts[ip_address] = []
        
        self.ip_attempts[ip_address].append({
            'timestamp': current_time,
            'reason': reason
        })

        # Clean old attempts (older than 1 hour)
        self._clean_old_attempts(ip_address)

        # Calculate threat level
        recent_attempts = len(self.ip_attempts[ip_address])
        
        if recent_attempts >= 10:
            return 'CRITICAL'
        elif recent_attempts >= 5:
            return 'HIGH'
        elif recent_attempts >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _clean_old_attempts(self, ip_address: str):
        """Remove attempts older than 1 hour"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        if ip_address in self.ip_attempts:
            self.ip_attempts[ip_address] = [
                attempt for attempt in self.ip_attempts[ip_address]
                if attempt['timestamp'] > one_hour_ago
            ]

    def get_threat_statistics(self) -> Dict:
        """Get statistics about current threats"""
        stats = {
            'total_ips_tracked': len(self.ip_attempts),
            'high_risk_ips': [],
            'total_attempts': 0
        }

        for ip, attempts in self.ip_attempts.items():
            attempt_count = len(attempts)
            stats['total_attempts'] += attempt_count
            if attempt_count >= 5:
                stats['high_risk_ips'].append({
                    'ip': ip,
                    'attempts': attempt_count
                })

        return stats

    def is_blocked_ip(self, ip_address: str, threshold: int = 10) -> bool:
        """Check if an IP should be blocked based on attempt threshold"""
        if ip_address not in self.ip_attempts:
            return False
        return len(self.ip_attempts[ip_address]) >= threshold
