from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class BottomTools(QWidget):
    action_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QWidget {
                background: rgba(20, 25, 45, 0.85);
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                padding: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e3c72, stop:1 #2a5298);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00c6ff, stop:1 #0072ff);
                transform: scale(1.02);
            }
        """)
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        tools = ["Install eTool", "Backup/Restore", "Unlock Device", 
                 "Flash Firmware", "Fix iOS", "FRP Bypass", "Transfer Data"]
        for tool in tools:
            btn = QPushButton(tool)
            btn.clicked.connect(lambda checked, t=tool: self.action_triggered.emit(t))
            layout.addWidget(btn)