from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from ui.sidebar import Sidebar
from ui.topbar import TopBar
from ui.device_panel import DevicePanel
from ui.bottom_tools import BottomTools
from core.device_detector import DeviceDetector
from core.license_manager import verify_license, is_feature_allowed
from core.exploit_manager import ExploitManager
from core.loader_manager import LoaderManager
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eTool - Mobile Unlock Tool")
        self.resize(1200, 800)
        
        # Check license first
        self.license_data = verify_license()
        if not self.license_data["valid"]:
            self.show_license_dialog()
            return
        
        # Initialize core components
        self.device_detector = DeviceDetector()
        self.exploit_manager = ExploitManager()
        self.loader_manager = LoaderManager()
        
        # Setup UI
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)
        
        middle_layout = QHBoxLayout()
        self.sidebar = Sidebar()
        self.device_panel = DevicePanel()
        middle_layout.addWidget(self.sidebar)
        middle_layout.addWidget(self.device_panel)
        main_layout.addLayout(middle_layout)
        
        self.bottom_tools = BottomTools()
        self.bottom_tools.action_triggered.connect(self.on_bottom_action)
        main_layout.addWidget(self.bottom_tools)
        
        # Auto‑refresh device info every 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_device_info)
        self.timer.start(2000)
        
        # Initial refresh
        self.refresh_device_info()
    
    def refresh_device_info(self):
        """Update device panel with current connection."""
        device = self.device_detector.detect_device()
        if device:
            self.device_panel.update_device_info(device)
        else:
            self.device_panel.show_no_device()
    
    def on_bottom_action(self, action_name):
        """Called when a bottom tool button is clicked."""
        # First, check if license allows this feature
        feature_map = {
            "FRP Bypass": "android_frp",
            "Unlock Device": "bootloader_unlock",
            "Flash Firmware": "flashing",
            "Fix iOS": "ios_passcode",
            "Backup/Restore": "backup",
            "Transfer Data": "data_transfer"
        }
        feature = feature_map.get(action_name)
        if feature and not is_feature_allowed(feature, self.license_data):
            self.device_panel.show_error(f"License does not allow {action_name}")
            return
        
        # Run the action in a thread to keep UI responsive
        self.worker_thread = ActionThread(action_name, self.device_detector, self.exploit_manager)
        self.worker_thread.result_signal.connect(self.on_action_finished)
        self.worker_thread.start()
    
    def on_action_finished(self, success, message):
        if success:
            self.device_panel.show_success(message)
        else:
            self.device_panel.show_error(message)
    
    def show_license_dialog(self):
        from ui.dialogs import LicenseDialog
        dlg = LicenseDialog(self.license_data["error"])
        if dlg.exec():
            # retry license verification
            self.license_data = verify_license()
            if self.license_data["valid"]:
                self.refresh_device_info()
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
            self.result_signal.emit(False, "No device connected")
            return
        
        if self.action == "FRP Bypass":
            success = self.exploit_manager.run_frp_bypass(device)
            msg = "FRP bypass done" if success else "FRP bypass failed"
        elif self.action == "Unlock Device":
            success = self.exploit_manager.unlock_bootloader(device)
            msg = "Device unlocked" if success else "Unlock failed"
        elif self.action == "Flash Firmware":
            # Use loader_manager to get firehose, then flash
            success = self.flash_firmware(device)
            msg = "Flashing completed" if success else "Flashing error"
        else:
            success = False
            msg = f"Action {self.action} not yet implemented"
        
        self.result_signal.emit(success, msg)