"""
Bottom Tools Panel - Action buttons for device operations
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class BottomTools(QWidget):
    """Bottom toolbar with action buttons for device operations"""
    
    action_triggered = pyqtSignal(str)  # Signal emitted when action button is clicked
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QWidget { 
                background:#ffffff; 
            }
            QPushButton {
                border:none;
                padding:10px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background:#f0f4ff;
            }
            QPushButton:pressed {
                background:#e0e8ff;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        tools = [
            ("📲 Install eTool", "install_etool"),
            ("💾 Backup/Restore", "backup_restore"),
            ("🔓 Unlock Device", "unlock_device"),
            ("⚡ Flash Firmware", "flash_firmware"),
            ("🍎 Fix iOS", "fix_ios"),
            ("🔐 FRP Bypass", "frp_bypass"),
            ("📤 Transfer Data", "transfer_data"),
        ]
        
        self.buttons = {}
        for label, action_id in tools:
            btn = QPushButton(label)
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(100)
            btn.clicked.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
            layout.addWidget(btn)
            self.buttons[action_id] = btn
        
        layout.addStretch()
    
    def enable_action(self, action_id: str, enabled: bool = True):
        """Enable or disable a specific action button"""
        if action_id in self.buttons:
            self.buttons[action_id].setEnabled(enabled)
    
    def enable_all(self, enabled: bool = True):
        """Enable or disable all action buttons"""
        for btn in self.buttons.values():
            btn.setEnabled(enabled)
