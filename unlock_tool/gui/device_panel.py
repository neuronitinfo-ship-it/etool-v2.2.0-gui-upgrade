"""
Device Panel - Displays connected device information
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont


class DevicePanel(QWidget):
    """Displays information about connected device"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Device info box
        self.device_box = QFrame()
        self.device_box.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        box_layout = QVBoxLayout(self.device_box)
        box_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        self.title = QLabel("📱 Connected Device")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title.setFont(title_font)
        box_layout.addWidget(self.title)
        
        # Info label
        self.info_label = QLabel("No device detected.\n\nConnect via USB and ensure drivers are installed.")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 10))
        box_layout.addWidget(self.info_label)
        
        layout.addWidget(self.device_box)
        layout.addStretch()
    
    def update_device_info(self, device: dict):
        """Update panel with device information"""
        if not device:
            self.show_no_device()
            return
        
        brand = device.get('brand', 'Unknown')
        model = device.get('model', '')
        mode = device.get('mode', 'unknown')
        platform = device.get('platform', 'android').upper()
        chipset = device.get('chipset', '?')
        
        text = f"""
Device: {brand} {model}
Platform: {platform}
Mode: {mode.upper()}
Chipset: {chipset}
Status: ✅ Connected
        """.strip()
        
        if 'battery' in device:
            battery = device['battery']
            text += f"\nBattery: {battery}%"
        
        if 'storage_free' in device and 'storage_total' in device:
            free = device['storage_free']
            total = device['storage_total']
            text += f"\nStorage: {free} / {total} GB"
        
        self.info_label.setText(text)
    
    def show_no_device(self):
        """Show no device message"""
        msg = """No device detected.

Please ensure:
• Device is connected via USB cable
• USB Debugging is enabled (Android)
• Trust is granted on device (iOS)
• Drivers are properly installed
        """.strip()
        self.info_label.setText(msg)
    
    def show_error(self, error_msg: str):
        """Display error message"""
        self.title.setText("❌ Device Error")
        self.info_label.setText(f"ERROR:\n{error_msg}")
    
    def show_success(self, success_msg: str):
        """Display success message"""
        self.title.setText("✅ Operation Success")
        self.info_label.setText(success_msg)
    
    def show_loading(self, operation: str):
        """Show loading state"""
        self.title.setText("⏳ Device Detection")
        self.info_label.setText(f"Scanning for devices...\n\n{operation}")
