import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List


class EmailNotifier:
    def __init__(self, smtp_server: str = "smtp.gmail.com", 
                 smtp_port: int = 587,
                 sender_email: str = None, 
                 sender_password: str = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_alert_email(self, recipient: str, log_entry: dict) -> bool:
        """
        Send security alert email
        Returns True if successful, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            print("[EmailNotifier] Email credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = f"🚨 Security Alert - {log_entry['reason']}"

            # Email body
            body = f"""
SECURITY ALERT NOTIFICATION
============================

Application ID: {log_entry['app_id']}
IP Address: {log_entry['ip_address']}
Operation: {log_entry['operation']}
Reason: {log_entry['reason']}
Action Taken: {log_entry['action']}

Query Details:
{log_entry['query']}

Please investigate this security incident immediately.

---
This is an automated message from the Database Security System.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"[EmailNotifier] Alert email sent to {recipient}")
            return True

        except Exception as e:
            print(f"[EmailNotifier] Failed to send email: {str(e)}")
            return False

    def send_bulk_alert(self, recipients: List[str], log_entry: dict) -> int:
        """
        Send alert to multiple recipients
        Returns the number of successful sends
        """
        success_count = 0
        for recipient in recipients:
            if self.send_alert_email(recipient, log_entry):
                success_count += 1
        return success_count

    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.sender_email and self.sender_password:
                    server.login(self.sender_email, self.sender_password)
            print("[EmailNotifier] Connection test successful")
            return True
        except Exception as e:
            print(f"[EmailNotifier] Connection test failed: {str(e)}")
            return False
