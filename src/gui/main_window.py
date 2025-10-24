# main_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit,
                             QLabel, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from core.firewall import DatabaseFirewall

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.firewall = DatabaseFirewall()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Database Security System")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Test query section
        query_layout = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("App ID")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Address")
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("SQL Query")
        self.op_combo = QComboBox()
        self.op_combo.addItems(['SELECT', 'INSERT', 'UPDATE', 'DELETE'])

        test_btn = QPushButton("Test Query")
        test_btn.clicked.connect(self.test_query)

        query_layout.addWidget(QLabel("App:"))
        query_layout.addWidget(self.app_input)
        query_layout.addWidget(QLabel("IP:"))
        query_layout.addWidget(self.ip_input)
        query_layout.addWidget(QLabel("Op:"))
        query_layout.addWidget(self.op_combo)
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(test_btn)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(
            ['App ID', 'IP', 'Operation', 'Reason', 'Query']
        )

        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.clicked.connect(self.refresh_logs)

        main_layout.addLayout(query_layout)
        main_layout.addWidget(QLabel("Results:"))
        main_layout.addWidget(self.results_text)
        main_layout.addWidget(refresh_btn)
        main_layout.addWidget(self.logs_table)

    def test_query(self):
        app_id = self.app_input.text()
        ip = self.ip_input.text()
        query = self.query_input.text()
        operation = self.op_combo.currentText()

        is_auth, results, reason = self.firewall.execute_query(
            app_id, ip, operation, query
        )

        status = "✅ AUTHORIZED" if is_auth else "❌ BLOCKED"
        self.results_text.setText(
            f"{status}\nReason: {reason}\nResults: {results}"
        )
        self.refresh_logs()

    def refresh_logs(self):
        logs = self.firewall.get_logs()
        self.logs_table.setRowCount(len(logs))

        for i, log in enumerate(logs):
            self.logs_table.setItem(i, 0, QTableWidgetItem(log['app_id']))
            self.logs_table.setItem(i, 1, QTableWidgetItem(log['ip_address']))
            self.logs_table.setItem(i, 2, QTableWidgetItem(log['operation']))
            self.logs_table.setItem(i, 3, QTableWidgetItem(log['reason']))
            self.logs_table.setItem(i, 4, QTableWidgetItem(log['query'][:50]))
