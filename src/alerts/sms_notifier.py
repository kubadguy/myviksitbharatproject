from typing import List


class SMSNotifier:
    def __init__(self, api_key: str = None, api_url: str = None):
        """
        Initialize SMS notifier with API credentials
        This is a placeholder for SMS service integration (Twilio, AWS SNS, etc.)
        """
        self.api_key = api_key
        self.api_url = api_url

    def send_sms_alert(self, phone_number: str, log_entry: dict) -> bool:
        """
        Send security alert via SMS
        Returns True if successful, False otherwise
        """
        if not self.api_key or not self.api_url:
            print("[SMSNotifier] SMS service not configured")
            return False

        try:
            # Format message (keep it short for SMS)
            message = (
                f"🚨 SECURITY ALERT\n"
                f"App: {log_entry['app_id']}\n"
                f"IP: {log_entry['ip_address']}\n"
                f"Reason: {log_entry['reason']}\n"
                f"Action: {log_entry['action']}"
            )

            # In a real implementation, you would call the SMS API here
            # Example with Twilio:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_='+1234567890',
            #     to=phone_number
            # )

            print(f"[SMSNotifier] SMS alert would be sent to {phone_number}")
            print(f"[SMSNotifier] Message: {message}")
            
            # Simulated success
            return True

        except Exception as e:
            print(f"[SMSNotifier] Failed to send SMS: {str(e)}")
            return False

    def send_bulk_sms(self, phone_numbers: List[str], log_entry: dict) -> int:
        """
        Send alert to multiple phone numbers
        Returns the number of successful sends
        """
        success_count = 0
        for phone in phone_numbers:
            if self.send_sms_alert(phone, log_entry):
                success_count += 1
        return success_count

    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Basic phone number validation
        """
        # Remove common formatting characters
        cleaned = phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Check if it's mostly digits and has reasonable length
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15

    def test_connection(self) -> bool:
        """Test SMS service connection"""
        if not self.api_key or not self.api_url:
            print("[SMSNotifier] SMS service not configured")
            return False
        
        print("[SMSNotifier] SMS service configuration OK (simulated)")
        return True
