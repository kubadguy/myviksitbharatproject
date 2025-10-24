class AlertManager:
    def __init__(self, email_enabled=True, sms_enabled=False):
        self.email_enabled = email_enabled
        self.sms_enabled = sms_enabled

    def send_alert(self, log_entry: dict):
        alert_msg = self._format_alert(log_entry)

        print("\n" + "="*60)
        print("🚨 SECURITY ALERT")
        print("="*60)
        print(alert_msg)
        print("="*60 + "\n")

        # Email/SMS would be sent here in production

    def _format_alert(self, log: dict) -> str:
        return f"""
Application:  {log['app_id']}
IP Address:   {log['ip_address']}
Operation:    {log['operation']}
Reason:       {log['reason']}
Query:        {log['query'][:100]}...
Action:       {log['action']}
"""
