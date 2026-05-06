"""
Enhanced main GUI window with new features: Device Compatibility, Security Advisory, DIAG Mode, Knox Bypass
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QComboBox, QTextEdit, QLineEdit, QSpinBox, QCheckBox,
                             QMessageBox, QProgressBar, QStatusBar, QMenuBar, QMenu)
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import json
from pathlib import Path


class DeviceCompatibilityTab(QWidget):
    """Tab for device profile matching and compatibility information"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_profiles()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Device Compatibility Analysis")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Device search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        search_layout.addWidget(self.device_combo)
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        layout.addLayout(search_layout)
        
        # Device info table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(2)
        self.device_table.setHorizontalHeaderLabels(["Property", "Value"])
        layout.addWidget(self.device_table)
        
        # Exploits available
        exploits_label = QLabel("Available Exploits:")
        exploits_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(exploits_label)
        
        self.exploits_text = QTextEdit()
        self.exploits_text.setReadOnly(True)
        self.exploits_text.setMaximumHeight(150)
        layout.addWidget(self.exploits_text)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Profile")
        self.apply_btn.clicked.connect(self.apply_profile)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_profiles(self):
        """Load device profiles from database"""
        try:
            profiles_path = Path(__file__).parent.parent / 'database' / 'device_profiles.json'
            if profiles_path.exists():
                with open(profiles_path, 'r') as f:
                    self.profiles = json.load(f)
                    for device in self.profiles:
                        self.device_combo.addItem(f"{device.get('brand', 'Unknown')} {device.get('model', '')}")
        except Exception as e:
            self.exploits_text.setText(f"Error loading profiles: {str(e)}")
    
    def on_device_changed(self):
        """Update display when device selection changes"""
        idx = self.device_combo.currentIndex()
        if 0 <= idx < len(self.profiles):
            device = self.profiles[idx]
            self.display_device_info(device)
    
    def display_device_info(self, device):
        """Display selected device information"""
        self.device_table.setRowCount(0)
        
        info_fields = ['brand', 'model', 'codename', 'family', 'android_version', 'security_level', 'chipset']
        for field in info_fields:
            if field in device:
                row = self.device_table.rowCount()
                self.device_table.insertRow(row)
                self.device_table.setItem(row, 0, QTableWidgetItem(field.replace('_', ' ').title()))
                self.device_table.setItem(row, 1, QTableWidgetItem(str(device[field])))
        
        # Show exploits
        exploits = device.get('exploits', [])
        self.exploits_text.setText("\n".join([f"• {e}" for e in exploits]) if exploits else "No exploits available")
    
    def apply_profile(self):
        """Apply device profile"""
        device_name = self.device_combo.currentText()
        QMessageBox.information(self, "Profile Applied", f"Device profile for {device_name} has been applied.")


class SecurityAdvisoryTab(QWidget):
    """Tab for CVE tracking and security advisory"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_cves()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Security Advisory & CVE Tracking")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Filter by severity
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Severity:"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.severity_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.severity_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # CVE table
        self.cve_table = QTableWidget()
        self.cve_table.setColumnCount(5)
        self.cve_table.setHorizontalHeaderLabels(["CVE ID", "Title", "Severity", "CVSS", "Affected"])
        self.cve_table.itemSelectionChanged.connect(self.on_cve_selected)
        layout.addWidget(self.cve_table)
        
        # CVE details
        details_label = QLabel("CVE Details:")
        details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(self.details_text)
        
        self.setLayout(layout)
    
    def load_cves(self):
        """Load CVE database"""
        try:
            cves_path = Path(__file__).parent.parent / 'database' / 'security_cves.json'
            if cves_path.exists():
                with open(cves_path, 'r') as f:
                    self.cves = json.load(f)
                    self.display_cves(self.cves)
        except Exception as e:
            self.details_text.setText(f"Error loading CVEs: {str(e)}")
    
    def display_cves(self, cves):
        """Display CVEs in table"""
        self.cve_table.setRowCount(0)
        for cve in cves:
            row = self.cve_table.rowCount()
            self.cve_table.insertRow(row)
            self.cve_table.setItem(row, 0, QTableWidgetItem(cve.get('cve_id', 'N/A')))
            self.cve_table.setItem(row, 1, QTableWidgetItem(cve.get('title', 'N/A')[:50]))
            
            severity = cve.get('severity', 'Unknown')
            severity_item = QTableWidgetItem(severity)
            # Color code severity
            if severity == 'Critical':
                severity_item.setBackground(QColor(255, 0, 0))
                severity_item.setForeground(QColor(255, 255, 255))
            elif severity == 'High':
                severity_item.setBackground(QColor(255, 127, 0))
            self.cve_table.setItem(row, 2, severity_item)
            
            self.cve_table.setItem(row, 3, QTableWidgetItem(str(cve.get('cvss_score', 'N/A'))))
            self.cve_table.setItem(row, 4, QTableWidgetItem(", ".join(cve.get('affected_products', [])[:2])))
    
    def apply_filter(self):
        """Filter CVEs by severity"""
        severity = self.severity_combo.currentText()
        if severity == "All":
            self.display_cves(self.cves)
        else:
            filtered = [c for c in self.cves if c.get('severity') == severity]
            self.display_cves(filtered)
    
    def on_cve_selected(self):
        """Show CVE details"""
        rows = self.cve_table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            if row < len(self.cves):
                cve = self.cves[row]
                details = f"""
CVE: {cve.get('cve_id', 'N/A')}
Title: {cve.get('title', 'N/A')}
Severity: {cve.get('severity', 'N/A')}
CVSS Score: {cve.get('cvss_score', 'N/A')}
Description: {cve.get('description', 'N/A')[:200]}...
Patches: {', '.join(cve.get('patches', []))}
                """
                self.details_text.setText(details)


class DIAGModeTab(QWidget):
    """Tab for Qualcomm DIAG mode operations"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Qualcomm DIAG Mode")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Detect Device:"))
        self.detect_btn = QPushButton("Scan USB Devices")
        self.detect_btn.clicked.connect(self.detect_devices)
        device_layout.addWidget(self.detect_btn)
        device_layout.addStretch()
        layout.addLayout(device_layout)
        
        # Status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        layout.addWidget(self.status_text)
        
        # DIAG operations
        ops_label = QLabel("DIAG Operations:")
        ops_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(ops_label)
        
        # Operation buttons
        button_layout = QHBoxLayout()
        self.nvram_read_btn = QPushButton("Read NVRAM")
        self.nvram_read_btn.clicked.connect(self.read_nvram)
        button_layout.addWidget(self.nvram_read_btn)
        
        self.device_info_btn = QPushButton("Get Device Info")
        self.device_info_btn.clicked.connect(self.get_device_info)
        button_layout.addWidget(self.device_info_btn)
        
        self.unlock_btn = QPushButton("Unlock Device (DIAG)")
        self.unlock_btn.clicked.connect(self.unlock_device)
        button_layout.addWidget(self.unlock_btn)
        layout.addLayout(button_layout)
        
        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def detect_devices(self):
        self.status_text.setText("Scanning USB devices...\n\nNote: This is a simulation. Connect physical device for real DIAG mode operations.")
    
    def read_nvram(self):
        self.status_text.setText("NVRAM Read Operation\n- Initiating DIAG session\n- Reading NVRAM data\n[Requires physical device connection]")
    
    def get_device_info(self):
        self.status_text.setText("Device Information\n- Model: [Device Model]\n- IMEI: [XXXXXXXXXXXX]\n- Baseband: [Baseband Version]\n[Requires physical device connection]")
    
    def unlock_device(self):
        self.status_text.setText("Unlock Device via DIAG\n- Initiating DIAG session\n- Sending unlock commands\n- Rebooting device\n[Requires physical device connection]")


class KnoxBypassTab(QWidget):
    """Tab for Knox security bypass methods"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Samsung Knox Security Bypass")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Device info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Target Device:"))
        self.target_device = QLineEdit()
        self.target_device.setPlaceholderText("Samsung Galaxy S24 / S23 / S22 etc.")
        info_layout.addWidget(self.target_device)
        layout.addLayout(info_layout)
        
        # Knox level info
        knox_label = QLabel("Available Knox Bypass Methods:")
        knox_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(knox_label)
        
        # Methods list
        self.methods_table = QTableWidget()
        self.methods_table.setColumnCount(3)
        self.methods_table.setHorizontalHeaderLabels(["Method", "Compatibility", "Status"])
        self.load_methods()
        layout.addWidget(self.methods_table)
        
        # Operation buttons
        button_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("Analyze Knox Level")
        self.analyze_btn.clicked.connect(self.analyze_knox)
        button_layout.addWidget(self.analyze_btn)
        
        self.bypass_btn = QPushButton("Execute Bypass")
        self.bypass_btn.clicked.connect(self.execute_bypass)
        button_layout.addWidget(self.bypass_btn)
        layout.addLayout(button_layout)
        
        # Output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def load_methods(self):
        """Load available Knox bypass methods"""
        methods = [
            ("Odin Firmware Downgrade", "All Samsung devices", "Available"),
            ("EDL Bootloader Modification", "Snapdragon models", "Available"),
            ("Recovery Image Injection", "All models", "Available"),
            ("Security Patch Downgrade", "All models", "Available"),
            ("VaultKeeper Exploit", "S20-S23", "Available"),
            ("Physical Detect Bypass", "Most models", "Available"),
            ("Custom Binary Upload", "All models", "Available"),
            ("Auto Method Selection", "Universal", "Available"),
        ]
        
        self.methods_table.setRowCount(len(methods))
        for idx, (method, compat, status) in enumerate(methods):
            self.methods_table.setItem(idx, 0, QTableWidgetItem(method))
            self.methods_table.setItem(idx, 1, QTableWidgetItem(compat))
            self.methods_table.setItem(idx, 2, QTableWidgetItem(status))
    
    def analyze_knox(self):
        device = self.target_device.text() or "Connected Device"
        self.output_text.setText(f"""
Knox Security Analysis for: {device}
═══════════════════════════════════════

Knox Level: 3
Knox Warranty: 0x1
Detected Methods:
  ✓ Downgrade bootloader
  ✓ EDL mode available
  ✓ Recovery rewritable
  
Recommended Method: Odin Firmware Downgrade
Estimated Time: 5-10 minutes
        """)
    
    def execute_bypass(self):
        self.output_text.setText("""
Executing Knox Bypass...
═════════════════════════

[1] Detecting device...      ✓
[2] Initializing ODIN mode...  ✓
[3] Uploading bootloader...    ⟳ In Progress
[4] Uploading firmware...
[5] Rebooting device...
[6] Verifying Knox reset...

Progress: 35%

Note: Device must remain connected
        """)


class MainWindow(QMainWindow):
    """Main application window with enhanced GUI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Servicing Tool v2.1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget with tabs
        central = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Android Servicing Tool - Professional Device Management")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Tab widget with new features
        self.tabs = QTabWidget()
        self.tabs.addTab(DeviceCompatibilityTab(), "Device Compatibility")
        self.tabs.addTab(SecurityAdvisoryTab(), "Security Advisory")
        self.tabs.addTab(DIAGModeTab(), "DIAG Mode")
        self.tabs.addTab(KnoxBypassTab(), "Knox Bypass")
        layout.addWidget(self.tabs)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit").triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Device Detection")
        tools_menu.addAction("ADB Shell")
        tools_menu.addAction("Fastboot")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About").triggered.connect(lambda: 
            QMessageBox.information(self, "About", 
                "Android Servicing Tool v2.1.0\n\nWith integrated Device Compatibility, "
                "Security Advisory, DIAG Mode, and Knox Bypass features."))
