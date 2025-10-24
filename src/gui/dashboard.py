from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class Dashboard(QWidget):
    def __init__(self, firewall):
        super().__init__()
        self.firewall = firewall
        self.init_ui()
        
        # Setup auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(2000)  # Refresh every 2 seconds

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Security Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Statistics Grid
        stats_layout = QGridLayout()
        
        # Stat cards
        self.total_queries_card = self.create_stat_card("Total Queries", "0")
        self.blocked_queries_card = self.create_stat_card("Blocked Queries", "0")
        self.honeypot_hits_card = self.create_stat_card("Honeypot Hits", "0")
        self.unique_ips_card = self.create_stat_card("Unique IPs", "0")

        stats_layout.addWidget(self.total_queries_card, 0, 0)
        stats_layout.addWidget(self.blocked_queries_card, 0, 1)
        stats_layout.addWidget(self.honeypot_hits_card, 1, 0)
        stats_layout.addWidget(self.unique_ips_card, 1, 1)

        layout.addLayout(stats_layout)

        # Recent Activity Section
        activity_label = QLabel("Recent Activity")
        activity_font = QFont()
        activity_font.setPointSize(12)
        activity_font.setBold(True)
        activity_label.setFont(activity_font)
        layout.addWidget(activity_label)

        self.activity_list = QLabel("No recent activity")
        self.activity_list.setWordWrap(True)
        self.activity_list.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        layout.addWidget(self.activity_list)

        layout.addStretch()
        self.setLayout(layout)

    def create_stat_card(self, title: str, value: str) -> QFrame:
        """Create a statistics card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        card_layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #333; font-size: 24px; font-weight: bold;")
        value_label.setObjectName("value_label")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)

        return card

    def refresh_stats(self):
        """Refresh dashboard statistics"""
        logs = self.firewall.get_logs()
        
        # Update statistics
        total_queries = len(logs)
        blocked_queries = sum(1 for log in logs if log['action'] == 'REDIRECTED_TO_HONEYPOT')
        
        # Get unique IPs
        unique_ips = len(set(log['ip_address'] for log in logs))

        # Update cards
        self.update_card_value(self.total_queries_card, str(total_queries))
        self.update_card_value(self.blocked_queries_card, str(blocked_queries))
        self.update_card_value(self.honeypot_hits_card, str(blocked_queries))
        self.update_card_value(self.unique_ips_card, str(unique_ips))

        # Update recent activity
        if logs:
            recent_logs = logs[-5:]  # Last 5 logs
            activity_text = ""
            for log in reversed(recent_logs):
                activity_text += f"• {log['app_id']} from {log['ip_address']}: {log['reason']}\n"
            self.activity_list.setText(activity_text)
        else:
            self.activity_list.setText("No recent activity")

    def update_card_value(self, card: QFrame, value: str):
        """Update the value label in a stat card"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
