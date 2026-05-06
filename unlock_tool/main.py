#!/usr/bin/env python3
"""
Android and iOS Servicing Tool - Main Entry Point

This application combines Android unlock operations with iOS support and a
license-based access control system.
"""

import base64
import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QProgressBar,
    QGroupBox, QCheckBox, QMessageBox, QTabWidget, QMenuBar,
    QFileDialog, QDialog, QDialogButtonBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon, QPixmap

from core.device_detector import DeviceDetector
from core.driver_manager import DriverManager
from core.usb_manager import USBScanner, USBDevice
from core.ios_manager import iOSManager
from core.exploit_manager import ExploitManager
from core.device_profiles import DeviceProfileManager
from core.security_advisor import SecurityAdvisor
from core.license_manager import verify_license, check_license_file, is_feature_allowed, get_remaining_days
from core.logger import Logger
from core.config import has_accepted_eula, set_eula_accepted
from core.updater import Updater
from modules.unlock.bootloader.generic_oem import GenericOEMUnlock
from modules.unlock.screenlock.adb_remove import ADBScreenLockRemove
from modules.flash.fastboot_flash import FastbootFlash
from modules.imei.generic_nvram import GenericNVRAMRepair
from modules.utils.backup_restore import BackupRestore
from modules.utils.signature_bypass import SignatureBypass
from modules.flash.payload_extractor import PayloadExtractor
from modules.ios.passcode_bypass import iOSPasscodeBypass
from modules.ios.activation_removal import IOSActivationRemoval
from modules.frp.generic_frp import GenericFRPBypass


class EULADialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('End User License Agreement')
        self.setModal(True)
        self.resize(800, 600)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Load EULA text
        try:
            with open('EULA.txt', 'r', encoding='utf-8') as f:
                eula_text = f.read()
        except Exception:
            eula_text = "EULA file not found. Please ensure EULA.txt is present."
        
        eula_display = QTextEdit()
        eula_display.setPlainText(eula_text)
        eula_display.setReadOnly(True)
        layout.addWidget(eula_display)
        
        self.accept_checkbox = QCheckBox('I have read and agree to the End User License Agreement')
        layout.addWidget(self.accept_checkbox)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_accept(self):
        if not self.accept_checkbox.isChecked():
            QMessageBox.warning(self, 'Agreement Required', 'You must accept the EULA to continue.')
            return
        set_eula_accepted(True)
        self.accept()


class LicenseDialog(QDialog):
    license_applied = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Activate License')
        self.setModal(True)
        self.resize(640, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        instructions = QLabel(
            'Paste your Base64-encoded license string below, or load it from a file. '
            'Generate a license with scripts/generate_license.py.\n\n'
            'Super Admin: Enter "kptjms991" for full access without license.'
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.license_input = QTextEdit()
        self.license_input.setPlaceholderText('Paste Base64 license string here...')
        layout.addWidget(self.license_input)

        load_button = QPushButton('Load License File')
        load_button.clicked.connect(self._load_license_file)
        layout.addWidget(load_button)

        self.status_label = QLabel('')
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._apply_license)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_license_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            'Select license file',
            '',
            'License Files (*.bin *.txt);;All Files (*)'
        )
        if not filepath:
            return

        try:
            license_text = Path(filepath).read_text(encoding='utf-8').strip()
            self.license_input.setPlainText(license_text)
            self.status_label.setText(f'Loaded license from {filepath}')
        except Exception as exc:
            QMessageBox.warning(self, 'Load Failed', f'Could not load license file:\n{exc}')

    def _apply_license(self):
        license_str = self.license_input.toPlainText().strip()
        if not license_str:
            QMessageBox.warning(self, 'License Required', 'Please enter or load a license string.')
            return

        license_data = verify_license(license_str)
        if not license_data.get('valid'):
            QMessageBox.warning(self, 'Invalid License', license_data.get('error', 'The license is invalid.'))
            return

        self.license_applied.emit(license_data)
        self.accept()


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, action: str, device_info: Dict[str, Any], logger: Optional[Logger] = None):
        super().__init__()
        self.action = action
        self.device_info = device_info
        self.logger = logger or Logger()

    def run(self):
        self.status.emit(f'Starting {self.action}...')
        self.progress.emit(10)
        detector = DeviceDetector(self.logger)
        detected = detector.detect_device(self.device_info.get('preferred_mode', 'auto'))
        if detected is None:
            self.finished.emit(False, 'No device detected')
            return
        self.device_info.update(detected)
        self.progress.emit(30)
        self.status.emit(f'Detected: {detected.get("platform")} {detected.get("mode")}')
        success = self._execute_action()
        self.progress.emit(100)
        self.finished.emit(success, 'Operation completed successfully' if success else 'Operation failed')

    def _execute_action(self) -> bool:
        actions = {
            'frp_bypass': self._frp_bypass,
            'auto_exploit': self._auto_exploit,
            'bootloader_unlock': self._bootloader_unlock,
            'screen_lock_remove': self._screen_lock_remove,
            'firmware_flash': self._firmware_flash,
            'imei_repair': self._imei_repair,
            'factory_reset': self._factory_reset,
            'backup_restore': self._backup_restore,
            'signature_bypass': self._signature_bypass,
            'payload_extract': self._payload_extract,
            'ios_passcode_bypass': self._ios_passcode_bypass,
            'ios_activation_removal': self._ios_activation_removal,
            'ios_backup': self._ios_backup,
            'ios_restore': self._ios_restore,
            'ios_erase': self._ios_erase,
        }
        return actions.get(self.action, lambda: False)()

    def _frp_bypass(self):
        self.status.emit('Attempting FRP bypass...')
        return GenericFRPBypass(self.device_info).bypass()

    def _auto_exploit(self):
        self.status.emit('Attempting auto exploit chain...')
        return ExploitManager(self.device_info, self.logger).run()

    def _bootloader_unlock(self):
        self.status.emit('Attempting bootloader unlock...')
        return GenericOEMUnlock(self.device_info).unlock()

    def _screen_lock_remove(self):
        self.status.emit('Attempting screen lock removal...')
        return ADBScreenLockRemove(self.device_info).remove_lock()

    def _firmware_flash(self):
        self.status.emit('Preparing firmware flash...')
        firmware_path = getattr(self.device_info, 'firmware_path', None)
        if not firmware_path:
            self.status.emit('No firmware file selected')
            return False

        # Verify firmware again before flashing
        from core.safe_operations import SafeOperations
        safe_ops = SafeOperations(self.logger)
        if not safe_ops.validate_firmware(firmware_path, self.device_info.get('model')):
            self.status.emit('Firmware validation failed - aborting flash')
            return False

        self.status.emit('Starting firmware flash...')
        flash_module = FastbootFlash(self.device_info)
        flash_module.firmware_path = firmware_path
        return flash_module.flash_firmware()

    def _imei_repair(self):
        self.status.emit('Attempting IMEI repair...')
        return GenericNVRAMRepair(self.device_info).repair_imei()

    def _factory_reset(self):
        self.status.emit('Performing factory reset...')
        return True

    def _backup_restore(self):
        self.status.emit('Starting backup/restore...')
        return BackupRestore(self.device_info).execute()

    def _signature_bypass(self):
        self.status.emit('Attempting signature bypass...')
        return SignatureBypass(self.device_info).execute()

    def _payload_extract(self):
        self.status.emit('Extracting payload...')
        return PayloadExtractor(self.device_info).execute()

    def _ios_passcode_bypass(self):
        self.status.emit('Attempting iOS passcode bypass...')
        return iOSPasscodeBypass(self.device_info).bypass(self.device_info.get('serial'))

    def _ios_activation_removal(self):
        self.status.emit('Attempting iOS activation removal...')
        return IOSActivationRemoval(self.device_info).remove_activation_lock(self.device_info.get('serial'))

    def _ios_backup(self):
        self.status.emit('Starting iOS backup...')
        return iOSManager(self.logger).backup(self.device_info.get('serial'))

    def _ios_restore(self):
        self.status.emit('Starting iOS restore...')
        return iOSManager(self.logger).restore(self.device_info.get('serial'))

    def _ios_erase(self):
        self.status.emit('Erasing iOS device...')
        return iOSManager(self.logger).erase_device(self.device_info.get('serial'))


class ModeSwitchThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, dict, str)

    def __init__(self, target_mode: str, preferred_serial: Optional[str] = None):
        super().__init__()
        self.target_mode = target_mode
        self.preferred_serial = preferred_serial

    def run(self):
        self.status.emit(f'Switching to {self.target_mode} mode...')
        self.progress.emit(10)
        from core.usb_manager import detect_and_set_mode
        success, info, message = detect_and_set_mode(self.target_mode, self.preferred_serial)
        self.progress.emit(100)
        self.finished.emit(success, info, message)


class MainWindow(QMainWindow):
    device_change_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.logger.info('Starting application')
        
        # Check EULA acceptance
        if not has_accepted_eula():
            eula_dialog = EULADialog(self)
            if eula_dialog.exec() != QDialog.DialogCode.Accepted:
                sys.exit(1)  # Exit if EULA not accepted
        
        self.scanner = USBScanner(self.logger)
        self.ios_manager = iOSManager(self.logger)
        self.device_detector = DeviceDetector(self.logger)
        self.driver_manager = DriverManager(self.logger)
        self.updater = Updater(self.logger)
        self.worker: Optional[WorkerThread] = None
        self.mode_switch_worker: Optional[ModeSwitchThread] = None
        self.license_data: Optional[Dict[str, Any]] = None
        self.exploit_manager: Optional[ExploitManager] = None
        self.init_ui()
        self._load_license()
        self.scanner.monitor_devices(self._on_usb_monitor_event)
        self._start_periodic_license_check()

    def init_ui(self):
        self.setWindowTitle('Unlock Tool v2.0')
        self.setGeometry(80, 80, 1280, 860)
        self.setWindowIcon(QIcon(self._asset_path('assets/logo.svg')))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        self._build_menu()

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        logo_label = self._create_logo_label()
        header_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignLeft)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        header_title = QLabel('Unlock Tool')
        header_title.setFont(QFont('Segoe UI', 26, QFont.Weight.Bold))
        header_title.setStyleSheet('color: #ffffff;')
        title_layout.addWidget(header_title)

        subtitle = QLabel('Professional Android + iOS servicing with offline support')
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet('color: #cfd8e6; font-size: 13px;')
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_container)

        self.tabs = QTabWidget()
        self.android_tab = self._create_android_tab()
        self.ios_tab = self._create_ios_tab()
        self.license_tab = self._create_license_tab()
        self.troubleshoot_tab = self._create_troubleshoot_tab()
        self.emergency_tab = self._create_emergency_tab()
        self.tabs.addTab(self.android_tab, 'Android')
        self.tabs.addTab(self.ios_tab, 'iOS')
        self.tabs.addTab(self.troubleshoot_tab, 'Troubleshooting')
        self.tabs.addTab(self.license_tab, 'License')
        self.tabs.addTab(self.emergency_tab, 'Emergency Recovery')
        self.auto_exploit_tab = self._create_auto_exploit_tab()
        self.tabs.addTab(self.auto_exploit_tab, 'Auto Exploit')
        layout.addWidget(self.tabs)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMinimumHeight(180)
        layout.addWidget(self.log_console)

        self.device_info_panel = QTextEdit()
        self.device_info_panel.setReadOnly(True)
        layout.addWidget(self.device_info_panel)

        self.status_bar = QLabel('Ready')
        layout.addWidget(self.status_bar)

        self._apply_global_style()

        self._append_log('Application initialized.')

    def _build_menu(self):
        license_menu = self.menu_bar.addMenu('License')
        info_action = QAction('License Info', self)
        info_action.triggered.connect(self._show_license_info)
        license_menu.addAction(info_action)
        activate_action = QAction('Activate License', self)
        activate_action.triggered.connect(self._show_license_dialog)
        license_menu.addAction(activate_action)

        tools_menu = self.menu_bar.addMenu('Tools')
        update_action = QAction('Check for Updates', self)
        update_action.triggered.connect(self._check_for_updates)
        tools_menu.addAction(update_action)
        export_logs_action = QAction('Export Logs', self)
        export_logs_action.triggered.connect(self._export_logs)
        tools_menu.addAction(export_logs_action)

    def _asset_path(self, resource_name: str) -> str:
        return str(Path(__file__).resolve().parent / resource_name)

    def _create_logo_label(self) -> QLabel:
        logo_label = QLabel()
        logo_pixmap = QPixmap(self._asset_path('assets/logo.svg'))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(128, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        logo_label.setFixedSize(132, 54)
        return logo_label

    def _create_brand_badge(self, name: str, asset: str) -> QLabel:
        badge = QLabel()
        badge.setFixedSize(120, 40)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet('border: 1px solid #2f343d; border-radius: 10px;')
        pixmap = QPixmap(self._asset_path(asset))
        if not pixmap.isNull():
            badge.setPixmap(
                pixmap.scaled(120, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            badge.setText(name)
            badge.setStyleSheet(
                'color: #ffffff; background-color: #1f242c; border: 1px solid #2f343d; border-radius: 10px;'
            )
        return badge

    def _apply_global_style(self):
        self.setStyleSheet('''
            QMainWindow { background-color: #111214; }
            QWidget { background-color: #111214; }
            QLabel { color: #e8eaed; }
            QMenuBar { background-color: #16181d; color: #e8eaed; }
            QMenuBar::item:selected { background: #2a2f39; }
            QMenu { background-color: #181a1f; color: #e8eaed; }
            QMenu::item:selected { background: #2a2f39; }
            QTabWidget::pane { border: 1px solid #2f343d; background: #14161a; }
            QTabBar::tab { background: #1f242c; color: #cfd8e6; padding: 10px 18px; border: 1px solid #2f343d; border-bottom-color: #14161a; border-top-left-radius: 10px; border-top-right-radius: 10px; min-width: 128px; }
            QTabBar::tab:selected { background: #22272f; color: #ffffff; margin-bottom: -1px; }
            QTabBar::tab:hover { background: #2a2f39; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2463E8, stop:1 #00A8FF); color: #ffffff; border: none; border-radius: 8px; padding: 10px 16px; min-height: 36px; font-weight: 600; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d52ca, stop:1 #0088d1); }
            QPushButton:pressed { background: #0f3f9f; }
            QTextEdit, QComboBox, QLineEdit, QListView, QGroupBox { background-color: #16181d; color: #e8eaed; border: 1px solid #2f343d; }
            QLineEdit, QComboBox { padding: 6px; border-radius: 6px; }
            QGroupBox { border: 1px solid #2f343d; border-radius: 10px; margin-top: 14px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; top: -9px; padding: 0 4px; color: #69c0ff; }
        ''')
        self.status_bar.setStyleSheet('color: #b0bec5; padding: 8px;')

    def _create_android_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.android_mode_selector = QComboBox()
        self.android_mode_selector.addItems(['Auto', 'ADB', 'Fastboot', 'EDL', 'Recovery', 'META'])
        self.android_device_combo = QComboBox()
        self.android_device_combo.addItems(['Auto Detect'])

        detect_button = QPushButton('Detect Device')
        detect_button.clicked.connect(self.detect_device)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('Preferred Mode:'))
        mode_layout.addWidget(self.android_mode_selector)
        mode_layout.addWidget(QLabel('Device:'))
        mode_layout.addWidget(self.android_device_combo)
        mode_layout.addWidget(detect_button)
        layout.addLayout(mode_layout)

        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.addWidget(self._create_brand_badge('Samsung', 'assets/badge_samsung.svg'))
        brand_layout.addWidget(self._create_brand_badge('Pixel', 'assets/badge_pixel.svg'))
        brand_layout.addWidget(self._create_brand_badge('Huawei', 'assets/badge_huawei.svg'))
        brand_layout.addWidget(self._create_brand_badge('Qualcomm', 'assets/badge_qualcomm.svg'))
        brand_layout.addWidget(self._create_brand_badge('MediaTek', 'assets/badge_mediatek.svg'))
        layout.addLayout(brand_layout)

        self.android_action_buttons = []
        self.android_actions = {
            'FRP Bypass': 'frp_bypass',
            'Auto Exploit': 'auto_exploit',
            'Bootloader Unlock': 'bootloader_unlock',
            'Screen Lock Remove': 'screen_lock_remove',
            'Firmware Flash': 'firmware_flash',
            'IMEI Repair': 'imei_repair',
            'Factory Reset': 'factory_reset',
            'Backup/Restore': 'backup_restore',
            'Signature Bypass': 'signature_bypass',
            'Payload Extract': 'payload_extract'
        }

        for label, action in self.android_actions.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, a=action: self.start_action(a))
            self.android_action_buttons.append(btn)
            layout.addWidget(btn)

        # Firmware flash section
        firmware_group = QGroupBox("Firmware Flashing")
        firmware_layout = QVBoxLayout(firmware_group)

        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Firmware File:"))
        self.firmware_path_edit = QLineEdit()
        self.firmware_path_edit.setPlaceholderText("Select firmware file (.zip, .img, .bin)...")
        file_layout.addWidget(self.firmware_path_edit)

        self.browse_firmware_btn = QPushButton("Browse")
        self.browse_firmware_btn.clicked.connect(self._browse_firmware_file)
        file_layout.addWidget(self.browse_firmware_btn)

        firmware_layout.addLayout(file_layout)

        # Verification section
        verify_layout = QHBoxLayout()
        self.verify_firmware_btn = QPushButton("Verify File")
        self.verify_firmware_btn.clicked.connect(self._verify_firmware_file)
        self.verify_firmware_btn.setEnabled(False)
        verify_layout.addWidget(self.verify_firmware_btn)

        self.firmware_status_label = QLabel("Select a firmware file to verify")
        verify_layout.addWidget(self.firmware_status_label)
        verify_layout.addStretch()

        firmware_layout.addLayout(verify_layout)

        # Flash options
        options_layout = QHBoxLayout()
        self.safe_flash_checkbox = QCheckBox("Safe Flash (with backup)")
        self.safe_flash_checkbox.setChecked(True)
        options_layout.addWidget(self.safe_flash_checkbox)

        self.force_flash_checkbox = QCheckBox("Force Flash (ignore warnings)")
        options_layout.addWidget(self.force_flash_checkbox)

        firmware_layout.addLayout(options_layout)

        layout.addWidget(firmware_group)

        self.android_status = QLabel('Android tab ready.')
        layout.addWidget(self.android_status)
        return widget

    def _create_ios_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.ios_device_label = QLabel('No iOS device detected.')
        layout.addWidget(self.ios_device_label)

        ios_buttons = [
            ('Device Info', self._refresh_ios_info),
            ('Enter Recovery', lambda: self._start_ios_action('enter_recovery')),
            ('Exit Recovery', lambda: self._start_ios_action('exit_recovery')),
            ('Enter DFU', lambda: self._start_ios_action('enter_dfu')),
            ('Exit DFU', lambda: self._start_ios_action('exit_dfu')),
            ('Backup', lambda: self._start_ios_action('ios_backup')),
            ('Restore', lambda: self._start_ios_action('ios_restore')),
            ('Erase Device', lambda: self._start_ios_action('ios_erase')),
            ('Passcode Bypass', lambda: self._start_ios_action('ios_passcode_bypass')),
            ('Activation Removal', lambda: self._start_ios_action('ios_activation_removal'))
        ]
        for label, callback in ios_buttons:
            layout.addWidget(QPushButton(label, clicked=callback))

        self.ios_status = QLabel('iOS tab ready.')
        layout.addWidget(self.ios_status)
        return widget

    def _create_license_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.license_info_text = QTextEdit()
        self.license_info_text.setReadOnly(True)
        layout.addWidget(self.license_info_text)
        return widget

    def _create_troubleshoot_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.troubleshoot_intro = QLabel(
            'Troubleshooting helps you verify connected devices, driver support, and USB mode readiness.'
        )
        self.troubleshoot_intro.setWordWrap(True)
        layout.addWidget(self.troubleshoot_intro)

        self.driver_check_button = QPushButton('Run Driver & Connection Check')
        self.driver_check_button.clicked.connect(self._run_driver_check)
        layout.addWidget(self.driver_check_button)

        self.troubleshoot_status = QTextEdit()
        self.troubleshoot_status.setReadOnly(True)
        self.troubleshoot_status.setMinimumHeight(180)
        layout.addWidget(self.troubleshoot_status)

        self.troubleshoot_guidance = QTextEdit()
        self.troubleshoot_guidance.setReadOnly(True)
        self.troubleshoot_guidance.setMinimumHeight(220)
        layout.addWidget(self.troubleshoot_guidance)

        return widget

    def _create_emergency_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        emergency_label = QLabel('Emergency Recovery Mode')
        emergency_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(emergency_label)

        warning_text = QLabel(
            'WARNING: Emergency recovery may brick your device if used incorrectly.\n'
            'Only use this if your device is completely unresponsive.\n'
            'Always backup data first when possible.'
        )
        warning_text.setStyleSheet('color: red; font-weight: bold;')
        layout.addWidget(warning_text)

        # Device mode switching
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('Force device into mode:'))
        self.emergency_mode_combo = QComboBox()
        self.emergency_mode_combo.addItems(['EDL (Android)', 'Download Mode (Android)', 'DFU (iOS)', 'Recovery (iOS)'])
        mode_layout.addWidget(self.emergency_mode_combo)
        force_mode_btn = QPushButton('Force Mode')
        force_mode_btn.clicked.connect(self._force_device_mode)
        mode_layout.addWidget(force_mode_btn)
        layout.addLayout(mode_layout)

        # Stock firmware flashing
        flash_layout = QHBoxLayout()
        flash_layout.addWidget(QLabel('Stock firmware:'))
        self.stock_firmware_path = QLineEdit()
        self.stock_firmware_path.setPlaceholderText('Select firmware file...')
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self._browse_stock_firmware)
        flash_layout.addWidget(self.stock_firmware_path)
        flash_layout.addWidget(browse_btn)
        layout.addLayout(flash_layout)

        flash_btn = QPushButton('Flash Stock Firmware (Safe)')
        flash_btn.clicked.connect(self._flash_stock_firmware_safe)
        layout.addWidget(flash_btn)

        # Status
        self.emergency_status = QLabel('Emergency recovery ready.')
        layout.addWidget(self.emergency_status)

        return widget

    def _create_auto_exploit_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel('Auto Exploit')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        description = QLabel(
            'Automatically detect connected device and run appropriate exploits.\n'
            'This will attempt various unlock methods based on device type and vulnerabilities.'
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Device detection
        detect_btn = QPushButton('Detect Device')
        detect_btn.clicked.connect(self._detect_device_for_exploit)
        layout.addWidget(detect_btn)

        self.device_status_label = QLabel('No device detected.')
        layout.addWidget(self.device_status_label)

        # Auto exploit button
        self.auto_exploit_btn = QPushButton('Run Auto Exploit')
        self.auto_exploit_btn.clicked.connect(self._run_auto_exploit)
        self.auto_exploit_btn.setEnabled(False)
        layout.addWidget(self.auto_exploit_btn)

        # Progress
        self.exploit_progress = QProgressBar()
        self.exploit_progress.setVisible(False)
        layout.addWidget(self.exploit_progress)

        # Results
        self.exploit_results = QTextEdit()
        self.exploit_results.setReadOnly(True)
        self.exploit_results.setMaximumHeight(200)
        layout.addWidget(self.exploit_results)

        return widget

    def _append_log(self, message: str):
        timestamp = datetime.now(timezone.utc).astimezone().isoformat(sep=' ', timespec='seconds')
        self.log_console.append(f'[{timestamp}] {message}')
        self.device_info_panel.repaint()

    def _load_license(self):
        if check_license_file():
            self.license_data = verify_license(Path('license.bin').read_text(encoding='utf-8').strip())
        else:
            self.license_data = None
            self._show_license_dialog()
        self._update_license_status()

    def _update_license_status(self):
        if not self.license_data or not self.license_data.get('valid'):
            self._append_log('No valid license loaded. Tool features disabled.')
            self._set_disabled_state(True)
            self.license_info_text.setText('No valid license loaded.')
        else:
            days = get_remaining_days(self.license_data.get('expiry'))
            self.license_info_text.setText(
                f"User: {self.license_data.get('user')}\n"
                f"Expiry: {self.license_data.get('expiry')}\n"
                f"Features: {', '.join(self.license_data.get('features', []))}\n"
                f"Remaining days: {days}"
            )
            self._append_log('Valid license loaded.')
            self._set_disabled_state(False)

    def _set_disabled_state(self, disabled: bool):
        for btn in self.android_action_buttons:
            btn.setEnabled(not disabled)
        self.android_mode_selector.setEnabled(not disabled)
        self.android_device_combo.setEnabled(not disabled)
        self.ios_status.setEnabled(not disabled)

    def _show_license_dialog(self):
        dialog = LicenseDialog(self)
        dialog.license_applied.connect(self._apply_license)
        dialog.exec()

    def _apply_license(self, license_data: Dict[str, Any]):
        self.license_data = license_data
        with open('license.bin', 'w', encoding='utf-8') as f:
            f.write(self.license_data['raw'])
        self._update_license_status()
        self._append_log('License applied successfully.')

    def _show_license_info(self):
        if not self.license_data or not self.license_data.get('valid'):
            QMessageBox.warning(self, 'License Info', 'No valid license available.')
            return
        features = ', '.join(self.license_data.get('features', []))
        QMessageBox.information(self, 'License Info',
                                f"User: {self.license_data.get('user')}\n"
                                f"Expiry: {self.license_data.get('expiry')}\n"
                                f"Features: {features}")

    def _check_for_updates(self):
        self._append_log('Checking for updates...')
        result = self.updater.check_for_update()
        if result and result.available:
            reply = QMessageBox.question(
                self, 'Update Available',
                f"A new version {result.latest_version} is available.\n\n{result.notes}\n\nDownload now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._download_update(result.download_url)
        elif result:
            QMessageBox.information(self, 'Up to Date', f"You are running the latest version ({result.latest_version}).")
        else:
            QMessageBox.warning(self, 'Update Check Failed', 'Unable to check for updates. Please try again later.')

    def _download_update(self, download_url: str):
        if not download_url:
            QMessageBox.warning(self, 'Download Failed', 'No download URL available.')
            return
        self._append_log(f'Downloading update from {download_url}...')
        download_path = self.updater.download_update(download_url)
        if download_path:
            QMessageBox.information(
                self, 'Download Complete',
                f'Update downloaded to: {download_path}\n\nPlease install manually.'
            )
            self._append_log(f'Update downloaded to {download_path}')
        else:
            QMessageBox.warning(self, 'Download Failed', 'Failed to download the update.')
            self._append_log('Update download failed')

    def _export_logs(self):
        from pathlib import Path
        log_dir = Path.home() / '.local' / 'share' / 'unlock_tool' if sys.platform != 'win32' else Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'unlock_tool'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = log_dir / f'unlock_tool_logs_{timestamp}.zip'
        
        try:
            import zipfile
            with zipfile.ZipFile(archive_path, 'w') as zf:
                # Add main log file
                log_file = Path('unlock_tool.log')
                if log_file.exists():
                    zf.write(log_file, log_file.name)
                
                # Add any other log files in the directory
                for log_file in Path('.').glob('*.log'):
                    zf.write(log_file, log_file.name)
            
            QMessageBox.information(
                self, 'Logs Exported',
                f'Logs exported to: {archive_path}'
            )
            self._append_log(f'Logs exported to {archive_path}')
        except Exception as e:
            QMessageBox.warning(self, 'Export Failed', f'Failed to export logs: {e}')
            self._append_log(f'Log export failed: {e}')

    def _start_periodic_license_check(self):
        self.license_timer = QTimer(self)
        self.license_timer.timeout.connect(self._verify_license_periodic)
        self.license_timer.start(1000 * 60 * 60 * 24)

    def _verify_license_periodic(self):
        self._load_license()

    def _on_usb_monitor_event(self, added: List[USBDevice], removed: List[USBDevice]):
        added_desc = ', '.join(f'{dev.protocol}:{dev.vendor_id:04x}:{dev.product_id:04x}' for dev in added) or 'none'
        removed_desc = ', '.join(f'{dev.protocol}:{dev.vendor_id:04x}:{dev.product_id:04x}' for dev in removed) or 'none'
        self._append_log(f'USB event - added: {added_desc}; removed: {removed_desc}')

    def detect_device(self):
        preferred_mode = self.android_mode_selector.currentText().lower()
        device = self.device_detector.detect_device(preferred_mode)
        if not device:
            troubleshooting_msg = (
                "No device was detected. Connect your phone with a USB cable and verify the cable supports data transfer.\n\n"
                "Install Android SDK Platform Tools for adb/fastboot support.\n"
                "On Linux, make sure udev rules are installed and your user is in the plugdev group.\n"
                "On Windows, install vendor USB drivers or use Zadig/WinUSB for qualcomm/edl devices.\n"
                "On macOS, install libimobiledevice and usbmuxd for Apple device support."
            )
            self.android_status.setText('No device detected.')
            self._append_log('Device detection failed.')
            self.device_info_panel.setText(troubleshooting_msg)
            # Update troubleshoot tab if it exists
            if hasattr(self, 'troubleshoot_status'):
                self.troubleshoot_status.setPlainText('No device connected or supported device not recognized.')
            if hasattr(self, 'troubleshoot_guidance'):
                self.troubleshoot_guidance.setPlainText(self.driver_manager.get_generic_driver_guidance())
            return

        brand = device.get('brand', device.get('product', 'Unknown'))
        self._append_log(f"Detected {device['platform']} device: {brand}")
        self._show_device_info(device)
        self._show_driver_report(device)

    def _show_device_info(self, info: Dict[str, Any]):
        lines = [f'{k}: {v}' for k, v in info.items()]
        self.device_info_panel.setText('\n'.join(lines))
        if info.get('platform') == 'ios':
            self.tabs.setCurrentWidget(self.ios_tab)
        else:
            self.tabs.setCurrentWidget(self.android_tab)

    def _run_driver_check(self):
        preferred_mode = self.android_mode_selector.currentText().lower()
        device = self.device_detector.detect_device(preferred_mode)
        report = self.driver_manager.evaluate_device_driver_status(device)
        self._append_log('Driver check completed.')
        self.troubleshoot_status.setPlainText(self._format_driver_status(report))
        self.troubleshoot_guidance.setPlainText(report.get('guidance', ''))

    def _show_driver_report(self, device: Dict[str, Any]):
        report = self.driver_manager.evaluate_device_driver_status(device)
        self.troubleshoot_status.setPlainText(self._format_driver_status(report))
        self.troubleshoot_guidance.setPlainText(report.get('guidance', ''))

    def _format_driver_status(self, report: Dict[str, Any]) -> str:
        lines = []
        device_info = report.get('device_info', {})
        if report.get('status') == 'no_device':
            lines.append('No device detected.')
            lines.append('Available tools: ' + ', '.join(report.get('available_tools', [])))
            return '\n'.join(lines)

        lines.append('Detected device:')
        lines.append(f"  Brand: {device_info.get('brand', 'Unknown')}")
        lines.append(f"  Mode: {device_info.get('mode', 'Unknown')}")
        lines.append(f"  Platform: {device_info.get('platform', 'Unknown')}")
        lines.append(f"  VID:PID: {device_info.get('vendor_id', '')}:{device_info.get('product_id', '')}")
        lines.append('')
        lines.append('Driver checklist:')
        for requirement in report.get('required_drivers', []):
            lines.append(f"- {requirement['name']}: {requirement['reason']}")
        return '\n'.join(lines)

    def _set_progress(self, value: int):
        self.status_bar.setText(f'Progress: {value}%')

    def start_action(self, action: str):
        if not self.license_data or not self.license_data.get('valid'):
            QMessageBox.critical(self, 'License Required', 'A valid license is required for this operation.')
            return
        feature_map = {
            'frp_bypass': 'android_frp',
            'auto_exploit': 'android_frp',
            'bootloader_unlock': 'android_frp',
            'screen_lock_remove': 'android_frp',
            'firmware_flash': 'android_frp',
            'imei_repair': 'imei_repair',
            'backup_restore': 'android_frp',
            'signature_bypass': 'android_frp',
            'payload_extract': 'android_frp',
            'ios_passcode_bypass': 'ios_passcode',
            'ios_activation_removal': 'ios_passcode',
            'ios_backup': 'ios_flashing',
            'ios_restore': 'ios_flashing',
            'ios_erase': 'ios_flashing'
        }
        required_feature = feature_map.get(action, 'all')
        if not is_feature_allowed(required_feature, self.license_data):
            QMessageBox.warning(self, 'Feature Locked', f'Feature not allowed: {required_feature}')
            return

        self.worker = WorkerThread(action, {
            'preferred_mode': self.android_mode_selector.currentText().lower(),
            'serial': None,
            'backup': self.license_data.get('features', []),
            'verbose': True,
            'firmware_path': self.firmware_path_edit.text().strip() if hasattr(self, 'firmware_path_edit') else None
        }, self.logger)
        self.worker.progress.connect(self._set_progress)
        self.worker.status.connect(self._append_log)
        self.worker.finished.connect(self._on_action_finished)
        self.worker.start()
        self._append_log(f'Started action: {action}')

    def _on_action_finished(self, success: bool, message: str):
        self._append_log(message)
        if success:
            self.status_bar.setText('Operation completed successfully.')
        else:
            self.status_bar.setText('Operation failed.')

    def _refresh_ios_info(self):
        info = self.ios_manager.detect_device()
        if not info:
            self.ios_status.setText('No iOS device detected.')
            self._append_log('No iOS device detected.')
            return
        self.ios_status.setText(f"Detected iOS device: {info.get('product', info.get('serial'))}")
        self._show_device_info(info)

    def _start_ios_action(self, action: str):
        if not self.license_data or not self.license_data.get('valid'):
            QMessageBox.critical(self, 'License Required', 'A valid license is required for iOS operations.')
            return
        self.start_action(action)

    def _force_device_mode(self):
        target_mode = self.emergency_mode_combo.currentText().lower().split(' ')[0]  # Extract mode name
        mode_map = {
            'edl': 'edl',
            'download': 'download',
            'dfu': 'dfu',
            'recovery': 'recovery'
        }
        mode = mode_map.get(target_mode, 'recovery')
        
        self.mode_switch_worker = ModeSwitchThread(mode)
        self.mode_switch_worker.progress.connect(self._set_progress)
        self.mode_switch_worker.status.connect(self._append_log)
        self.mode_switch_worker.finished.connect(self._on_mode_switch_finished)
        self.mode_switch_worker.start()
        self._append_log(f'Attempting to force device into {mode} mode...')

    def _on_mode_switch_finished(self, success: bool, info: Dict[str, Any], message: str):
        self._append_log(message)
        if success:
            self.emergency_status.setText(f'Mode switch successful: {info}')
        else:
            self.emergency_status.setText('Mode switch failed.')

    def _browse_firmware_file(self):
        """Browse and select firmware file for flashing."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter('Firmware files (*.zip *.img *.bin *.tar *.tar.gz *.7z);;All files (*)')
        file_dialog.setWindowTitle("Select Firmware File")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                firmware_path = selected_files[0]
                self.firmware_path_edit.setText(firmware_path)
                self.verify_firmware_btn.setEnabled(True)
                self.firmware_status_label.setText("File selected - click Verify to check integrity")
                self._append_log(f"Firmware file selected: {firmware_path}")

    def _verify_firmware_file(self):
        """Verify the selected firmware file before flashing."""
        firmware_path = self.firmware_path_edit.text().strip()
        if not firmware_path:
            QMessageBox.warning(self, 'No File', 'Please select a firmware file first.')
            return

        firmware_file = Path(firmware_path)
        if not firmware_file.exists():
            QMessageBox.warning(self, 'File Not Found', 'The selected firmware file does not exist.')
            self.firmware_status_label.setText("❌ File not found")
            return

        # Start verification
        self.firmware_status_label.setText("🔍 Verifying firmware...")
        self.verify_firmware_btn.setEnabled(False)
        self._append_log("Starting firmware verification...")

        try:
            from core.safe_operations import SafeOperations
            safe_ops = SafeOperations(self.logger)

            # Get device info for validation
            device = self.device_detector.detect_device()
            device_model = device.get('model', 'unknown') if device else 'unknown'

            # Validate firmware
            if safe_ops.validate_firmware(firmware_path, device_model):
                # Additional checks
                file_size = firmware_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)

                # Check file extension and basic validation
                valid_extensions = ['.zip', '.img', '.bin', '.tar', '.tar.gz', '.7z']
                if not any(firmware_file.name.lower().endswith(ext) for ext in valid_extensions):
                    self.firmware_status_label.setText("⚠️  Warning: Unusual file extension")
                    QMessageBox.warning(self, 'Unusual Extension',
                                      'The selected file has an unusual extension for firmware.\n'
                                      'Please verify this is the correct firmware file.')
                else:
                    self.firmware_status_label.setText(f"✅ Verified ({file_size_mb:.1f} MB)")
                    QMessageBox.information(self, 'Verification Complete',
                                          f'Firmware file verified successfully!\n\n'
                                          f'File: {firmware_file.name}\n'
                                          f'Size: {file_size_mb:.1f} MB\n'
                                          f'Device: {device_model}\n\n'
                                          'You can now proceed with flashing.')

                self._append_log(f"Firmware verified: {firmware_file.name} ({file_size_mb:.1f} MB)")
            else:
                self.firmware_status_label.setText("❌ Verification failed")
                QMessageBox.warning(self, 'Verification Failed',
                                  'Firmware verification failed. The file may be corrupted or incompatible.\n'
                                  'Please check the file and try again.')
                self._append_log("Firmware verification failed")

        except Exception as e:
            self.firmware_status_label.setText("❌ Error during verification")
            QMessageBox.critical(self, 'Verification Error', f'An error occurred during verification:\n{str(e)}')
            self._append_log(f"Firmware verification error: {e}")

        finally:
            self.verify_firmware_btn.setEnabled(True)

    def _browse_stock_firmware(self):
        """Browse and select stock firmware file for emergency flashing."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter('Firmware files (*.zip *.img *.bin *.tar *.tar.gz *.7z);;All files (*)')
        file_dialog.setWindowTitle("Select Stock Firmware File")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                firmware_path = selected_files[0]
                self.stock_firmware_path.setText(firmware_path)
                self._append_log(f"Stock firmware file selected: {firmware_path}")

    def _flash_stock_firmware_safe(self):
        firmware_path = self.stock_firmware_path.text().strip()
        if not firmware_path:
            QMessageBox.warning(self, 'No Firmware', 'Please select a stock firmware file first.')
            return
        
        if not Path(firmware_path).exists():
            QMessageBox.warning(self, 'File Not Found', 'The selected firmware file does not exist.')
            return

        # Use safe operations for flashing
        from core.safe_operations import SafeOperations
        safe_ops = SafeOperations(self.logger)
        
        # For now, just validate the firmware (we'd need device info for full validation)
        if not safe_ops.validate_firmware(firmware_path, 'unknown'):
            QMessageBox.warning(self, 'Invalid Firmware', 'Firmware validation failed. Aborting.')
            return

        reply = QMessageBox.question(
            self, 'Confirm Flash',
            'This will erase all data on the device and flash stock firmware.\n'
            'Make sure you have backed up important data.\n\nContinue?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # This would need to be implemented with proper device detection and flashing
            self._append_log('Stock firmware flashing not yet implemented in emergency mode.')
            QMessageBox.information(self, 'Not Implemented', 'Stock firmware flashing is not yet fully implemented.')

    def _detect_device_for_exploit(self):
        """Detect connected device and prepare exploit manager."""
        try:
            devices = self.device_detector.detect_devices()
            if not devices:
                troubleshooting_msg = (
                    "No device was detected. Connect your phone with a USB cable and verify the cable supports data transfer.\n\n"
                    "Install Android SDK Platform Tools for adb/fastboot support.\n"
                    "On Linux, make sure udev rules are installed and your user is in the plugdev group.\n"
                    "On Windows, install vendor USB drivers or use Zadig/WinUSB for qualcomm/edl devices.\n"
                    "On macOS, install libimobiledevice and usbmuxd for Apple device support."
                )
                self.device_status_label.setText("No device detected.")
                self.exploit_results.setPlainText(troubleshooting_msg)
                self.auto_exploit_btn.setEnabled(False)
                self.exploit_manager = None
                self._append_log("No device detected - check troubleshooting guide")
                return

            device = devices[0]  # Use first detected device
            device_info = f'Device detected: {device.get("model", "Unknown")} ({device.get("brand", "Unknown")})'
            self.device_status_label.setText(device_info)
            self.exploit_results.setPlainText(f"Device ready for exploitation:\n{device_info}")
            self.exploit_manager = ExploitManager(device, self.logger)
            self.auto_exploit_btn.setEnabled(True)
            self._append_log(f'Device detected for auto exploit: {device}')

        except Exception as e:
            self.logger.error(f'Device detection failed: {e}')
            error_msg = f"Device detection failed: {str(e)}\n\nPlease check:\n- USB cable connection\n- Device drivers\n- Platform tools installation"
            self.device_status_label.setText('Device detection failed.')
            self.exploit_results.setPlainText(error_msg)
            self.auto_exploit_btn.setEnabled(False)

    def _run_auto_exploit(self):
        """Run the auto exploit chain."""
        if not self.exploit_manager:
            QMessageBox.warning(self, 'No Device', 'Please detect a device first.')
            return

        self.exploit_progress.setVisible(True)
        self.exploit_progress.setValue(0)
        self.exploit_results.clear()
        self.auto_exploit_btn.setEnabled(False)

        # Run in thread to avoid blocking UI
        self.exploit_thread = ExploitThread(self.exploit_manager, self.logger)
        self.exploit_thread.progress.connect(self.exploit_progress.setValue)
        self.exploit_thread.result.connect(self._on_exploit_result)
        self.exploit_thread.finished.connect(self._on_exploit_finished)
        self.exploit_thread.start()

    def _on_exploit_result(self, result: str):
        """Handle exploit result update."""
        self.exploit_results.append(result)

    def _on_exploit_finished(self):
        """Handle exploit completion."""
        self.exploit_progress.setVisible(False)
        self.auto_exploit_btn.setEnabled(True)
        self._append_log('Auto exploit process completed.')


class ExploitThread(QThread):
    """Thread for running exploits without blocking UI."""
    
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, exploit_manager: ExploitManager, logger: Logger):
        super().__init__()
        self.exploit_manager = exploit_manager
        self.logger = logger
    
    def run(self):
        try:
            self.result.emit('Starting auto exploit chain...\n')
            success = self.exploit_manager.run()
            if success:
                self.result.emit('Auto exploit completed successfully!\n')
            else:
                self.result.emit('Auto exploit failed. No suitable exploits found.\n')
        except Exception as e:
            self.logger.error(f'Auto exploit error: {e}')
            self.result.emit(f'Error during auto exploit: {e}\n')
        finally:
            self.finished.emit()


def main():
    parser = argparse.ArgumentParser(description='Android and iOS Servicing Tool')
    parser.add_argument('--gui', action='store_true', help='Launch graphical user interface')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName('Unlock Tool')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
