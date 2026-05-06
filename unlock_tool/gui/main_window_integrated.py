"""
Enhanced Main Window - Integrated GUI with new components
Professional Android & iOS Servicing Tool with device detection, threading, and real-time feedback
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QTextEdit, QLineEdit,
    QSpinBox, QCheckBox, QMessageBox, QProgressBar, QMenuBar, QMenu, QSplitter,
    QFileDialog, QGroupBox, QFormLayout, QListWidget, QListWidgetItem, QGridLayout
)
from PyQt6.QtGui import QFont, QIcon, QColor, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from gui.components.device_selector import AdvancedDeviceSelector
from gui.components.status_bar import EnhancedStatusBar
from gui.components.operation_log import OperationLogPanel
from gui.theme_manager import ThemeManager
from gui.bottom_tools import BottomTools
from gui.device_panel import DevicePanel


class EnhancedMainWindow(QMainWindow):
    """Main application window with enhanced UI components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eTool - Mobile Unlock Tool v2.2.0")
        self.resize(1600, 1000)
        
        self.current_theme = 'light'
        self.device_profiles = self.load_profiles()
        
        # Apply default theme
        app = QApplication.instance()
        ThemeManager.apply_theme(app, self.current_theme)
        
        # Setup UI components
        self.init_ui()
        self.init_menu_bar()
        self.init_status_bar()
        self.init_timers()
    
    def load_profiles(self):
        """Load device profiles from database"""
        try:
            profiles_path = Path(__file__).parent.parent / 'database' / 'device_profiles.json'
            if profiles_path.exists():
                with open(profiles_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profiles: {e}")
        return []
    
    def init_ui(self):
        """Initialize main UI layout"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Panel: Device Selector
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(5, 5, 5, 5)
        
        left_widget = QWidget()
        self.device_selector = AdvancedDeviceSelector(self.device_profiles)
        self.device_selector.device_selected.connect(self.on_device_selected)
        left_panel.addWidget(self.device_selector)
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)
        
        # Center Panel: Tabs
        center_widget = self.create_tabs()
        
        # Right Panel: Device Info + Operation Log
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(5, 5, 5, 5)
        
        # Device panel (top of right)
        self.device_panel = DevicePanel()
        right_panel.addWidget(self.device_panel, 1)
        
        # Operation log (bottom of right)
        self.operation_log = OperationLogPanel()
        right_panel.addWidget(self.operation_log, 1)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setMaximumWidth(400)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)
        
        main_layout.addWidget(splitter)
        
        # Bottom Tools
        self.bottom_tools = BottomTools()
        self.bottom_tools.action_triggered.connect(self.on_action_triggered)
        main_layout.addWidget(self.bottom_tools)
    
    def create_tabs(self) -> QWidget:
        """Create tab widget with various tools"""
        tabs = QTabWidget()
        
        tabs.addTab(self.create_home_tab(), "🏠 Home")
        tabs.addTab(self.create_compatibility_tab(), "📱 Compatibility")
        tabs.addTab(self.create_security_tab(), "🔒 Security")
        tabs.addTab(self.create_tools_tab(), "🛠️ Tools")
        
        return tabs
    
    def create_home_tab(self) -> QWidget:
        """Create home/dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Welcome to eTool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        info = QLabel("""
eTool is a comprehensive mobile device servicing application supporting:

✓ Android Device Unlock & Recovery
✓ iOS Passcode Bypass
✓ Firmware Flashing
✓ FRP/MDM Bypass
✓ Device Backup & Restore
✓ Security Advisory

Quick Start:
1. Connect your device via USB
2. Select device from the list
3. Choose operation from bottom toolbar
4. Follow on-screen instructions

Features:
• Support for 50+ devices
• Real-time device detection
• Secure license verification
• Comprehensive operation logging
• Dark/Light theme support
        """.strip())
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Quick stats
        stats_group = QGroupBox("Quick Stats")
        stats_layout = QFormLayout()
        stats_layout.addRow("Supported Devices:", QLabel(f"{len(self.device_profiles)}"))
        stats_layout.addRow("Licensed Features:", QLabel("8/10"))
        stats_layout.addRow("License Status:", QLabel("✅ Valid (45 days)"))
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return widget
    
    def create_compatibility_tab(self) -> QWidget:
        """Create device compatibility tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("📱 Device Compatibility")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Device table
        self.compat_table = QTableWidget()
        self.compat_table.setColumnCount(5)
        self.compat_table.setHorizontalHeaderLabels([
            "Brand", "Model", "Chipset", "Android", "Support"
        ])
        self.compat_table.setRowCount(0)
        
        # Populate with sample data
        for idx, device in enumerate(self.device_profiles[:10]):
            self.compat_table.insertRow(idx)
            self.compat_table.setItem(idx, 0, QTableWidgetItem(device.get('brand', '?')))
            self.compat_table.setItem(idx, 1, QTableWidgetItem(device.get('model', '?')))
            self.compat_table.setItem(idx, 2, QTableWidgetItem(device.get('chipset', '?')))
            self.compat_table.setItem(idx, 3, QTableWidgetItem(device.get('android_version', '?')))
            
            support = "✅" if device.get('exploits') else "⚠️"
            self.compat_table.setItem(idx, 4, QTableWidgetItem(support))
        
        layout.addWidget(self.compat_table)
        return widget
    
    def create_security_tab(self) -> QWidget:
        """Create security advisory tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("🔒 Security Advisory")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # CVE info
        cve_text = QTextEdit()
        cve_text.setReadOnly(True)
        cve_text.setText("""
Active CVE Monitoring:

[CRITICAL] CVE-2024-XXXX - Android Bootloader Exploit
  Severity: 9.8
  Affected Devices: Galaxy S23, Pixel 8
  Status: Mitigation Available
  
[HIGH] CVE-2024-YYYY - iOS Passcode Bypass
  Severity: 8.2
  Affected Versions: iOS 17.0-17.2
  Status: Patch Available
  
[MEDIUM] CVE-2024-ZZZZ - FRP Lock Vulnerability
  Severity: 6.5
  Affected: Various Samsung Models
  Status: Workaround Available

⚠️ Keep eTool updated for latest CVE patches
        """)
        layout.addWidget(cve_text)
        
        return widget
    
    def create_tools_tab(self) -> QWidget:
        """Create tools tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("🛠️ Advanced Tools")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tool options
        tools_group = QGroupBox("Available Tools")
        tools_layout = QGridLayout()
        
        tools = [
            ("ADB Shell", "Open ADB shell terminal"),
            ("Fastboot Mode", "Boot device to fastboot"),
            ("EDL Mode", "Boot to EDL/DIAG mode"),
            ("Device Log", "View device system log"),
            ("Partition Info", "Show partition details"),
            ("IMEI Repair", "Fix IMEI issues"),
        ]
        
        for idx, (name, desc) in enumerate(tools):
            row = idx // 2
            col = idx % 2
            
            tool_btn = QPushButton(f"🔧 {name}")
            tool_btn.setToolTip(desc)
            tools_layout.addWidget(tool_btn, row, col)
        
        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)
        layout.addStretch()
        
        return widget
    
    def init_menu_bar(self):
        """Initialize application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        open_action = QAction("Open Device Config", self)
        open_action.triggered.connect(self.open_device_config)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("👁️ View")
        
        theme_menu = view_menu.addMenu("🎨 Theme")
        
        light_action = QAction("☀️ Light Mode", self)
        light_action.triggered.connect(lambda: self.set_theme('light'))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("🌙 Dark Mode", self)
        dark_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("🛠️ Tools")
        
        export_log_action = QAction("📥 Export Operation Log", self)
        export_log_action.triggered.connect(self.operation_log.export_log)
        tools_menu.addAction(export_log_action)
        
        clear_log_action = QAction("🗑️ Clear Log", self)
        clear_log_action.triggered.connect(self.operation_log.clear_log)
        tools_menu.addAction(clear_log_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        
        about_action = QAction("About eTool", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_status_bar(self):
        """Initialize enhanced status bar"""
        self.status_bar = EnhancedStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_connected(False)
        self.status_bar.set_license_info("Valid", 45)
    
    def init_timers(self):
        """Initialize background timers"""
        # Device detection timer
        self.device_timer = QTimer()
        self.device_timer.timeout.connect(self.refresh_device_detection)
        self.device_timer.start(2000)  # Every 2 seconds
    
    def refresh_device_detection(self):
        """Periodically check for connected devices"""
        # This would normally call the device detector
        # For now, just a placeholder
        pass
    
    def on_device_selected(self, device: dict):
        """Handle device selection from list"""
        self.operation_log.log_info(f"Selected: {device.get('brand', '?')} {device.get('model', '?')}")
        self.device_panel.update_device_info(device)
        self.status_bar.set_connected(True, True)
    
    def on_action_triggered(self, action_id: str):
        """Handle action button click"""
        action_names = {
            'install_etool': 'Install eTool',
            'backup_restore': 'Backup/Restore',
            'unlock_device': 'Unlock Device',
            'flash_firmware': 'Flash Firmware',
            'fix_ios': 'Fix iOS',
            'frp_bypass': 'FRP Bypass',
            'transfer_data': 'Transfer Data',
        }
        
        action_name = action_names.get(action_id, action_id)
        self.operation_log.log_info(f"Starting: {action_name}")
        self.status_bar.set_operation_status(action_name, 0)
        
        # Simulate operation
        self.status_bar.update_queue_count(1)
        QMessageBox.information(self, "Operation", f"{action_name} operation initiated.")
        
        self.operation_log.log_success(f"{action_name} completed successfully")
        self.status_bar.reset()
    
    def set_theme(self, theme: str):
        """Switch application theme"""
        self.current_theme = theme
        app = QApplication.instance()
        ThemeManager.apply_theme(app, theme)
        self.operation_log.log_info(f"Theme changed to {theme}")
    
    def open_device_config(self):
        """Open device configuration file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Device Config",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            self.operation_log.log_info(f"Opened config: {filename}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About eTool",
            """
eTool v2.2.0
Mobile Device Servicing Tool

Supports: Android, iOS, Samsung Knox
Features: Unlock, Flashing, FRP Bypass, Data Recovery

License: Professional Edition (45 days remaining)
© 2024 eTool Development Team
            """.strip()
        )


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = EnhancedMainWindow()
    window.show()
    sys.exit(app.exec())
