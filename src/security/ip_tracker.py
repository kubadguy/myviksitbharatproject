from typing import Dict, List
from datetime import datetime
import ipaddress


class IPTracker:
    def __init__(self):
        self.tracked_ips = {}
        self.blocked_ips = set()

    def track_ip(self, ip_address: str, app_id: str, operation: str):
        """Track an IP address activity"""
        if ip_address not in self.tracked_ips:
            self.tracked_ips[ip_address] = {
                'first_seen': datetime.now(),
                'last_seen': datetime.now(),
                'attempts': 0,
                'operations': [],
                'apps': set()
            }

        self.tracked_ips[ip_address]['last_seen'] = datetime.now()
        self.tracked_ips[ip_address]['attempts'] += 1
        self.tracked_ips[ip_address]['operations'].append({
            'operation': operation,
            'timestamp': datetime.now()
        })
        self.tracked_ips[ip_address]['apps'].add(app_id)

    def block_ip(self, ip_address: str):
        """Add an IP address to the block list"""
        self.blocked_ips.add(ip_address)

    def unblock_ip(self, ip_address: str):
        """Remove an IP address from the block list"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)

    def is_blocked(self, ip_address: str) -> bool:
        """Check if an IP address is blocked"""
        return ip_address in self.blocked_ips

    def get_ip_info(self, ip_address: str) -> Dict:
        """Get information about a specific IP address"""
        if ip_address not in self.tracked_ips:
            return None

        info = self.tracked_ips[ip_address].copy()
        info['apps'] = list(info['apps'])
        info['is_blocked'] = self.is_blocked(ip_address)
        return info

    def get_all_tracked_ips(self) -> List[Dict]:
        """Get information about all tracked IPs"""
        result = []
        for ip, info in self.tracked_ips.items():
            ip_data = {
                'ip_address': ip,
                'first_seen': info['first_seen'],
                'last_seen': info['last_seen'],
                'attempts': info['attempts'],
                'apps': list(info['apps']),
                'is_blocked': self.is_blocked(ip)
            }
            result.append(ip_data)
        return result

    def get_suspicious_ips(self, threshold: int = 5) -> List[str]:
        """Get IPs with attempts exceeding threshold"""
        suspicious = []
        for ip, info in self.tracked_ips.items():
            if info['attempts'] >= threshold:
                suspicious.append(ip)
        return suspicious

    def is_private_ip(self, ip_address: str) -> bool:
        """Check if an IP address is private"""
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            return ip_obj.is_private
        except:
            return False

    def clear_tracking(self):
        """Clear all tracking data"""
        self.tracked_ips = {}
        self.blocked_ips = set()
