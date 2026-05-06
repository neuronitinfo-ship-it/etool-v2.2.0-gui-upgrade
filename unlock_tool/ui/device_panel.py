from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QProgressBar

class DevicePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(30, 35, 55, 0.9);
                border-radius: 20px;
                padding: 20px;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 14px;
            }
            QProgressBar {
                border-radius: 8px;
                text-align: center;
                background: #2a2a3a;
                color: white;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c6ff, stop:1 #0072ff);
            }
        """)
        layout = QVBoxLayout(self)
        
        self.device_frame = QFrame()
        inner = QVBoxLayout(self.device_frame)
        
        self.title = QLabel("📱 Connected Device")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        inner.addWidget(self.title)
        
        self.info = QLabel("No device detected.\n\nConnect your phone via USB.")
        self.info.setWordWrap(True)
        inner.addWidget(self.info)
        
        self.battery_bar = QProgressBar()
        self.battery_bar.setVisible(False)
        self.battery_bar.setRange(0, 100)
        inner.addWidget(self.battery_bar)
        
        self.storage_bar = QProgressBar()
        self.storage_bar.setVisible(False)
        inner.addWidget(self.storage_bar)
        
        layout.addWidget(self.device_frame)
    
    def update_device_info(self, device):
        if not device:
            self.show_no_device()
            return
        text = f"""
<b>{device.get('brand', 'Unknown')} {device.get('model', '')}</b><br>
Mode: <b>{device.get('mode', '?')}</b><br>
Platform: {device.get('platform', 'android')}<br>
Chipset: {device.get('chipset', '?')}
        """
        self.info.setText(text)
        if 'battery' in device:
            self.battery_bar.setVisible(True)
            self.battery_bar.setValue(device['battery'])
            self.battery_bar.setFormat(f"🔋 Battery: {device['battery']}%")
        else:
            self.battery_bar.setVisible(False)
        if 'storage_free' in device:
            self.storage_bar.setVisible(True)
            used = device['storage_total'] - device['storage_free']
            percent = int(used / device['storage_total'] * 100)
            self.storage_bar.setValue(percent)
            self.storage_bar.setFormat(f"💾 Storage: {used:.1f} / {device['storage_total']} GB")
        else:
            self.storage_bar.setVisible(False)
    
    def show_no_device(self):
        self.info.setText("⚠️ No device connected.\n\nEnsure USB debugging is enabled (Android)\nor trust this computer (iOS).")
        self.battery_bar.setVisible(False)
        self.storage_bar.setVisible(False)
    
    def show_error(self, msg):
        self.info.setText(f"❌ ERROR\n{msg}")
        self.battery_bar.setVisible(False)
        self.storage_bar.setVisible(False)
    
    def show_success(self, msg):
        self.info.setText(f"✅ SUCCESS\n{msg}")