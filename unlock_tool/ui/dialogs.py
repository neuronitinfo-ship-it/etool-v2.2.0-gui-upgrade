from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit

class LicenseDialog(QDialog):
    def __init__(self, error_msg=""):
        super().__init__()
        self.setWindowTitle("License Required")
        self.resize(450, 300)
        self.setStyleSheet("""
            QDialog { background: #1e1e2e; }
            QLabel { color: white; font-size: 14px; }
            QTextEdit { background: #2a2a3a; color: white; border-radius: 8px; }
            QPushButton {
                background: #0f3460; color: white; border-radius: 8px;
                padding: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1a5f7a; }
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter your license key:"))
        self.license_input = QTextEdit()
        self.license_input.setPlaceholderText("Paste license here...")
        layout.addWidget(self.license_input)
        self.error_label = QLabel(error_msg)
        self.error_label.setStyleSheet("color: #ff6666;")
        layout.addWidget(self.error_label)
        ok_btn = QPushButton("Activate")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Reminder")
        self.resize(400, 200)
        self.setStyleSheet("background: #1e1e2e; color: white;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("✅ Device connected!\n\nIf unstable, check USB cable or try another port."))
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)