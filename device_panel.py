class DevicePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.device_box = QFrame()
        self.device_box.setStyleSheet("QFrame { background:white; border-radius:10px; padding:15px; }")
        box_layout = QVBoxLayout(self.device_box)
        self.title = QLabel("Connected Device")
        self.title.setStyleSheet("font-size:18px; font-weight:bold;")
        self.info_label = QLabel("No device detected.\n\nConnect via USB and ensure drivers are installed.")
        self.info_label.setWordWrap(True)
        box_layout.addWidget(self.title)
        box_layout.addWidget(self.info_label)
        layout.addWidget(self.device_box)
    
    def update_device_info(self, device):
        text = f"""
Device: {device.get('brand', 'Unknown')} {device.get('model', '')}
Mode: {device.get('mode', 'unknown')}
Platform: {device.get('platform', 'android')}
Chipset: {device.get('chipset', '?')}
Status: Connected
        """
        if 'battery' in device:
            text += f"Battery: {device['battery']}%\n"
        if 'storage_free' in device:
            text += f"Storage: {device['storage_free']} / {device['storage_total']} GB"
        self.info_label.setText(text)
    
    def show_no_device(self):
        self.info_label.setText("No device detected.\n\nPlease connect your phone and allow USB debugging (Android) or trust the computer (iOS).")
    
    def show_error(self, msg):
        self.info_label.setText(f"❌ ERROR\n{msg}")
    
    def show_success(self, msg):
        self.info_label.setText(f"✅ SUCCESS\n{msg}")