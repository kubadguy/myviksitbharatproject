"""
Database Connection Manager for GUI
Allows users to connect to and manage different databases
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLabel, QLineEdit, QPushButton, QComboBox,
                              QTableWidget, QTableWidgetItem, QMessageBox,
                              QFileDialog, QSpinBox, QTextEdit, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.adapters import (SQLiteAdapter, PostgreSQLAdapter, 
                                MySQLAdapter, MongoDBAdapter)
from database_protection.transparent_wrapper import (
    install_transparent_wrapper, 
    uninstall_transparent_wrapper,
    is_protection_enabled,
    set_app_id
)


class DatabaseConnectionTab(QWidget):
    """Widget for managing database connections"""
    
    connection_changed = pyqtSignal(object)  # Signal when connection changes
    
    def __init__(self, firewall=None):
        super().__init__()
        self.firewall = firewall
        self.current_adapter = None
        self.connections = {}  # Store multiple connections
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Database Connection Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Create tabs for different sections
        tabs = QTabWidget()
        
        # Connection tab
        connection_tab = self.create_connection_tab()
        tabs.addTab(connection_tab, "Connect to Database")
        
        # Active connections tab
        active_tab = self.create_active_connections_tab()
        tabs.addTab(active_tab, "Active Connections")
        
        # Query executor tab
        query_tab = self.create_query_tab()
        tabs.addTab(query_tab, "Execute Queries")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def create_connection_tab(self):
        """Create the database connection configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Database type selection
        type_group = QGroupBox("Database Type")
        type_layout = QHBoxLayout()
        
        type_layout.addWidget(QLabel("Select Type:"))
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(['SQLite', 'PostgreSQL', 'MySQL', 'MongoDB'])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)
        type_layout.addStretch()
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Connection parameters (will change based on DB type)
        self.params_group = QGroupBox("Connection Parameters")
        self.params_layout = QVBoxLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Initialize with SQLite parameters
        self.on_db_type_changed('SQLite')
        
        # Connection name and app ID
        config_group = QGroupBox("Security Configuration")
        config_layout = QVBoxLayout()
        
        # Connection name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Connection Name:"))
        self.conn_name_input = QLineEdit()
        self.conn_name_input.setPlaceholderText("e.g., Production DB")
        name_layout.addWidget(self.conn_name_input)
        config_layout.addLayout(name_layout)
        
        # App ID
        app_layout = QHBoxLayout()
        app_layout.addWidget(QLabel("Application ID:"))
        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("e.g., webapp_frontend")
        app_layout.addWidget(self.app_id_input)
        config_layout.addLayout(app_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.setStyleSheet("background-color: #28a745;")
        connect_btn.clicked.connect(self.connect_database)
        button_layout.addWidget(connect_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlaceholderText("Connection status will appear here...")
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def on_db_type_changed(self, db_type):
        """Handle database type change"""
        # Clear existing parameters
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Store input widgets
        self.param_inputs = {}
        
        if db_type == 'SQLite':
            self.create_sqlite_params()
        elif db_type == 'PostgreSQL':
            self.create_postgresql_params()
        elif db_type == 'MySQL':
            self.create_mysql_params()
        elif db_type == 'MongoDB':
            self.create_mongodb_params()
    
    def create_sqlite_params(self):
        """Create SQLite connection parameters"""
        # Database file path
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Database File:"))
        self.param_inputs['database'] = QLineEdit()
        self.param_inputs['database'].setPlaceholderText("Path to .db file")
        file_layout.addWidget(self.param_inputs['database'])
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_sqlite_file)
        file_layout.addWidget(browse_btn)
        
        self.params_layout.addLayout(file_layout)
    
    def create_postgresql_params(self):
        """Create PostgreSQL connection parameters"""
        params = [
            ('host', 'Host:', 'localhost'),
            ('port', 'Port:', '5432'),
            ('database', 'Database:', 'postgres'),
            ('user', 'Username:', 'postgres'),
            ('password', 'Password:', '')
        ]
        
        for key, label, placeholder in params:
            layout = QHBoxLayout()
            layout.addWidget(QLabel(label))
            self.param_inputs[key] = QLineEdit()
            self.param_inputs[key].setPlaceholderText(placeholder)
            
            if key == 'password':
                self.param_inputs[key].setEchoMode(QLineEdit.EchoMode.Password)
            
            layout.addWidget(self.param_inputs[key])
            self.params_layout.addLayout(layout)
    
    def create_mysql_params(self):
        """Create MySQL connection parameters"""
        params = [
            ('host', 'Host:', 'localhost'),
            ('port', 'Port:', '3306'),
            ('database', 'Database:', 'mysql'),
            ('user', 'Username:', 'root'),
            ('password', 'Password:', '')
        ]
        
        for key, label, placeholder in params:
            layout = QHBoxLayout()
            layout.addWidget(QLabel(label))
            self.param_inputs[key] = QLineEdit()
            self.param_inputs[key].setPlaceholderText(placeholder)
            
            if key == 'password':
                self.param_inputs[key].setEchoMode(QLineEdit.EchoMode.Password)
            
            layout.addWidget(self.param_inputs[key])
            self.params_layout.addLayout(layout)
    
    def create_mongodb_params(self):
        """Create MongoDB connection parameters"""
        params = [
            ('host', 'Host:', 'localhost'),
            ('port', 'Port:', '27017'),
            ('database', 'Database:', 'test'),
            ('user', 'Username (optional):', ''),
            ('password', 'Password (optional):', '')
        ]
        
        for key, label, placeholder in params:
            layout = QHBoxLayout()
            layout.addWidget(QLabel(label))
            self.param_inputs[key] = QLineEdit()
            self.param_inputs[key].setPlaceholderText(placeholder)
            
            if key == 'password':
                self.param_inputs[key].setEchoMode(QLineEdit.EchoMode.Password)
            
            layout.addWidget(self.param_inputs[key])
            self.params_layout.addLayout(layout)
    
    def browse_sqlite_file(self):
        """Browse for SQLite database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite Database",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if file_path:
            self.param_inputs['database'].setText(file_path)
    
    def get_connection_config(self):
        """Get connection configuration from inputs"""
        config = {}
        for key, widget in self.param_inputs.items():
            value = widget.text()
            
            # Convert port to int if applicable
            if key == 'port' and value:
                try:
                    config[key] = int(value)
                except ValueError:
                    config[key] = value
            else:
                config[key] = value
        
        return config
    
    def test_connection(self):
        """Test database connection"""
        db_type = self.db_type_combo.currentText()
        config = self.get_connection_config()
        
        self.status_text.append(f"\n[INFO] Testing {db_type} connection...")
        
        try:
            adapter = self.create_adapter(db_type, config)
            
            if adapter.connect():
                success, message = adapter.test_connection()
                
                if success:
                    self.status_text.append(f"[SUCCESS] {message}")
                    QMessageBox.information(self, "Success", f"Connection successful!\n{message}")
                else:
                    self.status_text.append(f"[ERROR] {message}")
                    QMessageBox.warning(self, "Connection Failed", message)
                
                adapter.disconnect()
            else:
                self.status_text.append("[ERROR] Failed to establish connection")
                QMessageBox.warning(self, "Connection Failed", "Could not connect to database")
        
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.status_text.append(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def connect_database(self):
        """Connect to database and store connection"""
        db_type = self.db_type_combo.currentText()
        config = self.get_connection_config()
        conn_name = self.conn_name_input.text() or f"{db_type} Connection"
        app_id = self.app_id_input.text() or "unknown_app"
        
        self.status_text.append(f"\n[INFO] Connecting to {db_type}...")
        
        try:
            adapter = self.create_adapter(db_type, config)
            
            if adapter.connect():
                # Store connection
                self.connections[conn_name] = {
                    'adapter': adapter,
                    'db_type': db_type,
                    'app_id': app_id,
                    'config': config
                }
                
                self.current_adapter = adapter
                
                self.status_text.append(f"[SUCCESS] Connected to {conn_name}")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully connected to {conn_name}\nApp ID: {app_id}"
                )
                
                # Update active connections display
                self.update_active_connections()
                
                # Emit signal
                self.connection_changed.emit(adapter)
            else:
                self.status_text.append("[ERROR] Failed to connect")
                QMessageBox.warning(self, "Connection Failed", "Could not connect to database")
        
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            self.status_text.append(f"[ERROR] {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def create_adapter(self, db_type, config):
        """Create appropriate database adapter"""
        if db_type == 'SQLite':
            return SQLiteAdapter(config)
        elif db_type == 'PostgreSQL':
            return PostgreSQLAdapter(config)
        elif db_type == 'MySQL':
            return MySQLAdapter(config)
        elif db_type == 'MongoDB':
            return MongoDBAdapter(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def create_active_connections_tab(self):
        """Create tab showing active connections"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Active Database Connections:"))
        
        # Connections table
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels([
            'Connection Name', 'Database Type', 'App ID', 'Status'
        ])
        self.connections_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.connections_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.connections_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_active_connections)
        button_layout.addWidget(refresh_btn)
        
        disconnect_btn = QPushButton("Disconnect Selected")
        disconnect_btn.setStyleSheet("background-color: #dc3545;")
        disconnect_btn.clicked.connect(self.disconnect_selected)
        button_layout.addWidget(disconnect_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def update_active_connections(self):
        """Update the active connections display"""
        self.connections_table.setRowCount(len(self.connections))
        
        for i, (name, conn_info) in enumerate(self.connections.items()):
            self.connections_table.setItem(i, 0, QTableWidgetItem(name))
            self.connections_table.setItem(i, 1, QTableWidgetItem(conn_info['db_type']))
            self.connections_table.setItem(i, 2, QTableWidgetItem(conn_info['app_id']))
            
            # Check connection status
            adapter = conn_info['adapter']
            status = "Connected" if adapter.is_connected() else "Disconnected"
            status_item = QTableWidgetItem(status)
            
            if status == "Connected":
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.connections_table.setItem(i, 3, status_item)
    
    def disconnect_selected(self):
        """Disconnect selected connection"""
        current_row = self.connections_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a connection to disconnect")
            return
        
        conn_name = self.connections_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Disconnect",
            f"Disconnect from '{conn_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if conn_name in self.connections:
                self.connections[conn_name]['adapter'].disconnect()
                del self.connections[conn_name]
                
                self.update_active_connections()
                QMessageBox.information(self, "Success", f"Disconnected from {conn_name}")
    
    def create_query_tab(self):
        """Create query execution tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Query input
        layout.addWidget(QLabel("Enter SQL Query:"))
        
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("SELECT * FROM users;")
        self.query_input.setMaximumHeight(150)
        layout.addWidget(self.query_input)
        
        # Execute button
        exec_btn = QPushButton("Execute Query (Protected)")
        exec_btn.setStyleSheet("background-color: #28a745; font-weight: bold;")
        exec_btn.clicked.connect(self.execute_query)
        layout.addWidget(exec_btn)
        
        # Results
        layout.addWidget(QLabel("Query Results:"))
        
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        
        widget.setLayout(layout)
        return widget
    
    def execute_query(self):
        """Execute query through the firewall"""
        query = self.query_input.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a query to execute")
            return
        
        if not self.current_adapter:
            QMessageBox.warning(self, "No Connection", "Please connect to a database first")
            return
        
        # Get app_id from current connection
        app_id = "unknown_app"
        for conn_name, conn_info in self.connections.items():
            if conn_info['adapter'] == self.current_adapter:
                app_id = conn_info['app_id']
                break
        
        try:
            # Execute through firewall if available
            if self.firewall:
                operation = query.split()[0].upper()
                is_auth, results, reason = self.firewall.execute_query(
                    app_id=app_id,
                    ip_address='127.0.0.1',
                    operation=operation,
                    query=query
                )
                
                if is_auth:
                    self.display_results(results, f"Query executed successfully")
                else:
                    self.display_results(results, f"BLOCKED: {reason}\n(Showing honeypot data)")
            else:
                # Execute directly if no firewall
                results = self.current_adapter.execute_query(query)
                self.display_results(results, "Query executed (no firewall protection)")
        
        except Exception as e:
            QMessageBox.critical(self, "Query Error", f"Error executing query:\n{str(e)}")
    
    def display_results(self, results, message):
        """Display query results in table"""
        if not results:
            QMessageBox.information(self, "Query Results", f"{message}\nNo results returned")
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Convert results to list of dicts if needed
        if isinstance(results[0], dict):
            # Results are already dicts (from adapters)
            columns = list(results[0].keys())
            rows = results
        else:
            # Results are tuples (from SQLite)
            columns = [f"Column {i+1}" for i in range(len(results[0]))]
            rows = [dict(zip(columns, row)) for row in results]
        
        # Setup table
        self.results_table.setRowCount(len(rows))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Populate table
        for i, row in enumerate(rows):
            for j, col in enumerate(columns):
                value = str(row.get(col, ''))
                self.results_table.setItem(i, j, QTableWidgetItem(value))
        
        self.results_table.resizeColumnsToContents()
        
        QMessageBox.information(self, "Success", f"{message}\nRows returned: {len(results)}")