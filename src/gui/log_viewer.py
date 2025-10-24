from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class LogViewer(QWidget):
    def __init__(self, firewall):
        super().__init__()
        self.firewall = firewall
        self.all_logs = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Security Logs Viewer")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All', 'App ID', 'IP Address', 'Reason'])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter value...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_logs)
        filter_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        filter_layout.addWidget(clear_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(6)
        self.logs_table.setHorizontalHeaderLabels([
            'Timestamp', 'App ID', 'IP Address', 'Operation', 'Reason', 'Query'
        ])
        self.logs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.logs_table.setColumnWidth(0, 150)
        self.logs_table.setColumnWidth(1, 120)
        self.logs_table.setColumnWidth(2, 120)
        self.logs_table.setColumnWidth(3, 80)
        self.logs_table.setColumnWidth(4, 200)
        self.logs_table.setColumnWidth(5, 300)
        
        layout.addWidget(self.logs_table)

        # Log count
        self.log_count_label = QLabel("Total logs: 0")
        layout.addWidget(self.log_count_label)

        self.setLayout(layout)
        self.refresh_logs()

    def refresh_logs(self):
        """Refresh the logs table from the firewall"""
        from datetime import datetime
        
        self.all_logs = self.firewall.get_logs()
        self.apply_filter()

    def apply_filter(self):
        """Apply the current filter to the logs"""
        filter_type = self.filter_combo.currentText()
        filter_value = self.filter_input.text().lower()

        # Filter logs
        if filter_type == 'All' or not filter_value:
            filtered_logs = self.all_logs
        else:
            filtered_logs = []
            for log in self.all_logs:
                if filter_type == 'App ID' and filter_value in log['app_id'].lower():
                    filtered_logs.append(log)
                elif filter_type == 'IP Address' and filter_value in log['ip_address'].lower():
                    filtered_logs.append(log)
                elif filter_type == 'Reason' and filter_value in log['reason'].lower():
                    filtered_logs.append(log)

        # Update table
        self.populate_table(filtered_logs)
        self.log_count_label.setText(f"Total logs: {len(filtered_logs)} (Filtered from {len(self.all_logs)})")

    def populate_table(self, logs):
        """Populate the table with logs"""
        from datetime import datetime
        
        self.logs_table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            # Add timestamp (simulated as current time for display)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logs_table.setItem(i, 0, QTableWidgetItem(timestamp))
            
            # Add log data
            self.logs_table.setItem(i, 1, QTableWidgetItem(log['app_id']))
            self.logs_table.setItem(i, 2, QTableWidgetItem(log['ip_address']))
            self.logs_table.setItem(i, 3, QTableWidgetItem(log['operation']))
            self.logs_table.setItem(i, 4, QTableWidgetItem(log['reason']))
            self.logs_table.setItem(i, 5, QTableWidgetItem(log['query'][:100] + '...' if len(log['query']) > 100 else log['query']))

            # Color code rows based on threat level
            if 'SQL injection' in log['reason']:
                color = QColor(255, 200, 200)  # Light red for injection attempts
            elif 'not whitelisted' in log['reason']:
                color = QColor(255, 230, 200)  # Light orange for unauthorized IPs
            else:
                color = QColor(255, 255, 200)  # Light yellow for other issues

            for col in range(6):
                item = self.logs_table.item(i, col)
                if item:
                    item.setBackground(color)

    def on_filter_changed(self, value):
        """Handle filter type change"""
        if value == 'All':
            self.filter_input.setEnabled(False)
            self.filter_input.clear()
        else:
            self.filter_input.setEnabled(True)
        self.apply_filter()

    def clear_logs(self):
        """Clear all logs"""
        self.firewall.logger.clear_logs()
        self.refresh_logs()
