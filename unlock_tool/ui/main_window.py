from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from ui.topbar import TopBar
from ui.sidebar import Sidebar
from ui.device_panel import DevicePanel
from ui.bottom_tools import BottomTools
from core.device_detector import DeviceDetector
from core.license_manager import verify_license, is_feature_allowed
from core.exploit_manager import ExploitManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eTool - Mobile Unlock & Repair")
        self.resize(1300, 850)
        
        # Global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Poppins', sans-serif;
            }
            QPushButton {
                font-family: 'Segoe UI', 'Poppins', sans-serif;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QFrame {
                background-color: rgba(30, 30, 46, 0.7);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            QScrollArea { border: none; }
        """)
        
        # License check
        self.license_data = verify_license()
        if not self.license_data["valid"]:
            self.show_license_dialog()
            return
        
        # Backend init
        self.device_detector = DeviceDetector()
        self.exploit_manager = ExploitManager()
        
        # Main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)
        
        # Middle: sidebar + device panel
        middle = QHBoxLayout()
        middle.setContentsMargins(10, 10, 10, 10)
        self.sidebar = Sidebar()
        self.device_panel = DevicePanel()
        middle.addWidget(self.sidebar)
        middle.addWidget(self.device_panel, stretch=1)
        main_layout.addLayout(middle)
        
        # Bottom action bar
        self.bottom_tools = BottomTools()
        self.bottom_tools.action_triggered.connect(self.on_bottom_action)
        main_layout.addWidget(self.bottom_tools)
        
        # Auto-refresh device
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_device)
        self.timer.start(2000)
        self.refresh_device()
    
    def refresh_device(self):
        device = self.device_detector.detect_device()
        self.device_panel.update_device_info(device)
    
    def on_bottom_action(self, action):
        # License feature check
        feature_map = {
            "FRP Bypass": "android_frp",
            "Unlock Device": "bootloader_unlock",
            "Flash Firmware": "flashing",
            "Fix iOS": "ios_passcode",
            "Backup/Restore": "backup",
        }
        feature = feature_map.get(action)
        if feature and not is_feature_allowed(feature, self.license_data):
            self.device_panel.show_error(f"License does not allow {action}")
            return
        
        # Run in thread
        self.worker = ActionThread(action, self.device_detector, self.exploit_manager)
        self.worker.result_signal.connect(self.on_action_finished)
        self.worker.start()
    
    def on_action_finished(self, success, message):
        if success:
            self.device_panel.show_success(message)
        else:
            self.device_panel.show_error(message)
    
    def show_license_dialog(self):
        from ui.dialogs import LicenseDialog
        dlg = LicenseDialog(self.license_data["error"])
        if dlg.exec():
            self.license_data = verify_license()
            if self.license_data["valid"]:
                self.refresh_device()
            else:
                sys.exit(1)
        else:
            sys.exit(0)

class ActionThread(QThread):
    result_signal = pyqtSignal(bool, str)
    def __init__(self, action, detector, exploit_manager):
        super().__init__()
        self.action = action
        self.detector = detector
        self.exploit_manager = exploit_manager
    
    def run(self):
        device = self.detector.detect_device()
        if not device:
            self.result_signal.emit(False, "No device connected.")
            return
        if self.action == "FRP Bypass":
            ok = self.exploit_manager.run_frp_bypass(device)
            msg = "FRP bypassed" if ok else "FRP bypass failed"
        elif self.action == "Unlock Device":
            ok = self.exploit_manager.unlock_bootloader(device)
            msg = "Device unlocked" if ok else "Unlock failed"
        elif self.action == "Flash Firmware":
            ok = self.exploit_manager.flash_firmware(device)
            msg = "Flashing done" if ok else "Flashing error"
        else:
            ok, msg = False, "Not implemented"
        self.result_signal.emit(ok, msg)