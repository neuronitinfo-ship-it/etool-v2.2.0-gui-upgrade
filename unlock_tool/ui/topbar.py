from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3460, stop:1 #1a5f7a);
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.2);
                border-radius: 8px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("eTool")
        logo.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        layout.addWidget(logo)
        layout.addStretch()
        
        for text in ["iDevice", "Android", "Flash", "Toolbox", "About"]:
            btn = QPushButton(text)
            layout.addWidget(btn)