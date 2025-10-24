from datetime import datetime
from typing import List, Tuple
import ipaddress

class AccessControl:
    def __init__(self, config):
        self.config = config

    def is_authorized(self, app_id: str, ip_address: str,
                     operation: str, current_time: datetime = None) -> Tuple[bool, str]:
        if current_time is None:
            current_time = datetime.now()

        if app_id not in self.config:
            return False, "Unknown application"

        app_config = self.config[app_id]

        # Check time window
        if not self._check_time_window(current_time, app_config['time_windows']):
            return False, "Outside authorized time window"

        # Check operation
        if operation.upper() not in app_config['allowed_operations']:
            return False, "Unauthorized operation"

        # Check IP whitelist
        if not self._check_ip_whitelist(ip_address, app_config['ip_whitelist']):
            return False, "IP not whitelisted"

        return True, "Authorized"

    def _check_time_window(self, current_time: datetime,
                          windows: List[Tuple[int, int]]) -> bool:
        current_hour = current_time.hour
        for start, end in windows:
            if start <= current_hour < end:
                return True
        return False

    def _check_ip_whitelist(self, ip: str, whitelist: List[str]) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip)
            for allowed in whitelist:
                if '/' in allowed:
                    if ip_obj in ipaddress.ip_network(allowed):
                        return True
                else:
                    if str(ip_obj) == allowed:
                        return True
            return False
        except:
            return False
