from PyQt6.QtCore import pyqtSignal

class BottomTools(QWidget):
    action_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # ... (same style) ...
        tools = ["Install eTool", "Backup/Restore", "Unlock Device", 
                 "Flash Firmware", "Fix iOS", "FRP Bypass", "Transfer Data"]
        for tool in tools:
            btn = QPushButton(tool)
            btn.clicked.connect(lambda checked, t=tool: self.action_triggered.emit(t))
            layout.addWidget(btn)