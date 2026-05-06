"""
Enhanced Status Bar - Real-time operation status with indicators
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class EnhancedStatusBar(QStatusBar):
    """Real-time operation status bar with indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize status bar components"""
        
        # Connection indicator (LED)
        self.connection_led = QLabel("●")
        self.connection_led.setStyleSheet("color: red; font-size: 14px; margin: 0 5px;")
        self.addPermanentWidget(self.connection_led)
        
        # Status text
        self.status_text = QLabel("Ready")
        self.status_text.setMinimumWidth(150)
        self.addPermanentWidget(self.status_text)
        
        # Operation queue badge
        self.queue_badge = QLabel("Queue: 0")
        self.queue_badge.setStyleSheet("""
            background-color: #FF6B6B;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
            margin: 0 5px;
        """)
        self.queue_badge.setVisible(False)
        self.addPermanentWidget(self.queue_badge)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)
        
        # License info
        self.license_info = QLabel("License: Valid")
        self.license_info.setMinimumWidth(150)
        self.addPermanentWidget(self.license_info)
    
    def set_connected(self, connected: bool, stable: bool = True):
        """Update connection indicator"""
        if connected:
            color = "green" if stable else "orange"
            tooltip = "Device connected" if stable else "Connection unstable"
        else:
            color = "red"
            tooltip = "Device disconnected"
        
        self.connection_led.setStyleSheet(f"color: {color}; font-size: 14px; margin: 0 5px;")
        self.connection_led.setToolTip(tooltip)
    
    def set_operation_status(self, operation: str, progress: int = 0):
        """Update operation status"""
        self.status_text.setText(f"Op: {operation}")
        
        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
        
        if progress == 100:
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)
    
    def update_queue_count(self, count: int):
        """Update operation queue counter"""
        if count > 0:
            self.queue_badge.setText(f"Queue: {count}")
            self.queue_badge.setVisible(True)
        else:
            self.queue_badge.setVisible(False)
    
    def set_license_info(self, status: str, days_remaining: int = None):
        """Update license information"""
        if days_remaining is not None:
            self.license_info.setText(f"License: {status} ({days_remaining}d)")
        else:
            self.license_info.setText(f"License: {status}")
        
        self.license_info.setToolTip(f"License status: {status}")
    
    def reset(self):
        """Reset status bar to default state"""
        self.status_text.setText("Ready")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.queue_badge.setVisible(False)
        self.set_connected(False)
