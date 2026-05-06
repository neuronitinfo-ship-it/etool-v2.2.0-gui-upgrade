from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QWidget {
                background: rgba(20, 25, 45, 0.85);
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                background: transparent;
                color: #dddddd;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3460, stop:1 #1a5f7a);
                color: white;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        
        menu = ["Info", "Apps", "Photos", "Music", "Videos", "Files", 
                "Android Tools", "iOS Tools", "Settings"]
        for item in menu:
            btn = QPushButton(f"  {item}")
            layout.addWidget(btn)
        layout.addStretch()