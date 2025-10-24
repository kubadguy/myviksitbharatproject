"""
Enhanced Main Window for Database Security System GUI
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QPushButton, QLabel, QStatusBar,
                              QToolBar, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon
import json
from datetime import datetime

# Import other GUI components
from gui.dashboard import Dashboard
from gui.log_viewer import LogViewer
from gui.database_connection_tab import DatabaseConnectionTab


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.firewall = None  # Will be set by main.py
        self.tabs_initialized = False
        self.init_ui()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(500)  # Check more frequently initially
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Database Security System - Enhanced Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid #007bff;
            }
        """)
        
        # Wait for firewall to be set before creating tabs
        # We'll create them in refresh_data
        main_layout.addWidget(self.tabs)
        
        # Create status bar
        self.create_status_bar()
        
        # Apply stylesheet
        self.apply_stylesheet()
    
    def create_toolbar(self):
        """Create toolbar with actions"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Clear logs action
        clear_action = QAction("Clear Logs", self)
        clear_action.triggered.connect(self.clear_logs)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def create_header(self):
        """Create header section"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; padding: 20px;")
        layout = QVBoxLayout(header)
        
        title = QLabel("Database Security System")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        subtitle = QLabel("Real-time Database Access Monitoring & Protection")
        subtitle.setStyleSheet("color: #ecf0f1; font-size: 14px;")
        layout.addWidget(subtitle)
        
        return header
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Connection status
        self.connection_status = QLabel("Firewall Active")
        self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.connection_status)
    
    def apply_stylesheet(self):
        """Apply modern stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QLabel {
                color: #333333;
            }
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #cccccc;
                spacing: 10px;
                padding: 5px;
            }
        """)
    
    def refresh_data(self):
        """Refresh all data displays"""
        if self.firewall is None:
            # Firewall not set yet, try to import it
            try:
                from core.firewall import DatabaseFirewall
                self.firewall = DatabaseFirewall()
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
                return
        
        # Initialize tabs if not done yet
        if not self.tabs_initialized:
            self.initialize_tabs()
            self.tabs_initialized = True
            # Slow down refresh after initialization
            self.refresh_timer.setInterval(3000)
        
        # Update status
        try:
            logs = self.firewall.get_logs()
            self.status_label.setText(f"Total Events: {len(logs)} | Active")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def initialize_tabs(self):
        """Initialize tabs once firewall is available"""
        if self.firewall is None:
            return
            
        try:
            # Database Connection tab (NEW!)
            self.db_connection_tab = DatabaseConnectionTab(self.firewall)
            self.tabs.addTab(self.db_connection_tab, "Database Connections")
            
            # Dashboard tab
            self.dashboard = Dashboard(self.firewall)
            self.tabs.addTab(self.dashboard, "Dashboard")
            
            # Logs tab
            self.log_viewer = LogViewer(self.firewall)
            self.tabs.addTab(self.log_viewer, "Security Logs")
            
            self.status_label.setText("Tabs initialized successfully")
        except Exception as e:
            self.status_label.setText(f"Error initializing tabs: {str(e)}")
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize tabs:\n{str(e)}")
    
    def clear_logs(self):
        """Clear all security logs"""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear all security logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.firewall:
                self.firewall.logger.clear_logs()
                self.refresh_data()
                QMessageBox.information(self, "Success", "Logs cleared successfully")
    
    def export_data(self):
        """Export security logs to file"""
        if not self.firewall:
            QMessageBox.warning(self, "No Data", "No firewall data available to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Security Logs",
            f"security_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                logs = self.firewall.get_logs()
                
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(logs, f, indent=2)
                elif file_path.endswith('.csv'):
                    import csv
                    if logs:
                        with open(file_path, 'w', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                            writer.writeheader()
                            writer.writerows(logs)
                
                QMessageBox.information(self, "Success", f"Logs exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting logs:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Database Security System</h2>
        <p><b>Version 1.0</b></p>
        <p>A comprehensive database security solution with:</p>
        <ul>
            <li>Real-time SQL injection detection</li>
            <li>Access control and authorization</li>
            <li>Honeypot database for attackers</li>
            <li>Detailed security logging</li>
            <li>Multi-database support (SQLite, PostgreSQL, MySQL, MongoDB)</li>
            <li>Application-level access control</li>
        </ul>
        <p><b>Built with Python and PyQt6</b></p>
        <p>&copy; 2025 Database Security System</p>
        """
        
        QMessageBox.about(self, "About Database Security System", about_text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?\n\nAll active database connections will be closed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Close all database connections
            if hasattr(self, 'db_connection_tab'):
                for conn_info in self.db_connection_tab.connections.values():
                    try:
                        conn_info['adapter'].disconnect()
                    except:
                        pass
            event.accept()
        else:
            event.ignore()