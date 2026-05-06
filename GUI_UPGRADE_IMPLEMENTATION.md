# UI Upgrade Implementation Guide - Code Examples

## 🔧 Quick Implementation Templates

### 1. Enhanced Search & Filter Component

```python
# unlock_tool/gui/components/device_selector.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class AdvancedDeviceSelector(QWidget):
    """Enhanced device selection with search, filters, and favorites"""
    
    device_selected = pyqtSignal(dict)
    
    def __init__(self, profiles):
        super().__init__()
        self.profiles = profiles
        self.favorites = set()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by brand, model, or codename...")
        self.search_input.textChanged.connect(self.filter_devices)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        self.filter_brand = QPushButton("Brand ▼")
        self.filter_security = QPushButton("Security ▼")
        self.filter_chipset = QPushButton("Chipset ▼")
        self.show_favorites = QCheckBox("⭐ Favorites Only")
        
        filter_layout.addWidget(self.filter_brand)
        filter_layout.addWidget(self.filter_security)
        filter_layout.addWidget(self.filter_chipset)
        filter_layout.addWidget(self.show_favorites)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Device list
        self.device_list = QListWidget()
        self.device_list.itemDoubleClicked.connect(self.on_device_selected)
        layout.addWidget(self.device_list)
        
        self.setLayout(layout)
        self.populate_devices()
    
    def populate_devices(self):
        """Load all devices into list"""
        for device in self.profiles:
            item_text = f"{device.get('brand', '')} {device.get('model', '')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)
    
    def filter_devices(self, search_text):
        """Filter devices based on search query"""
        search_lower = search_text.lower()
        
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            text = item.text().lower()
            device = item.data(Qt.ItemDataRole.UserRole)
            
            matches_search = any([
                search_lower in text,
                search_lower in device.get('codename', '').lower(),
                search_lower in device.get('chipset', '').lower()
            ])
            
            item.setHidden(not matches_search)
    
    def toggle_favorite(self, device):
        """Add/remove device from favorites"""
        key = f"{device['brand']}-{device['model']}"
        if key in self.favorites:
            self.favorites.remove(key)
        else:
            self.favorites.add(key)
    
    def on_device_selected(self, item):
        """Emit signal when device selected"""
        device = item.data(Qt.ItemDataRole.UserRole)
        self.device_selected.emit(device)
```

---

### 2. Dark Mode Theme Manager

```python
# unlock_tool/gui/theme_manager.py

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    """Manages light and dark themes"""
    
    THEMES = {
        'light': {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F7FB',
            'fg_primary': '#1A1A1A',
            'fg_secondary': '#666666',
            'accent': '#1E6DFB',
            'accent_dark': '#0B4FD1',
            'success': '#22C55E',
            'error': '#EF4444',
            'warning': '#F59E0B',
        },
        'dark': {
            'bg_primary': '#1E1E1E',
            'bg_secondary': '#2D2D2D',
            'fg_primary': '#FFFFFF',
            'fg_secondary': '#CCCCCC',
            'accent': '#4A9EFF',
            'accent_dark': '#2E7FE6',
            'success': '#4ADE80',
            'error': '#F87171',
            'warning': '#FBBF24',
        }
    }
    
    @staticmethod
    def apply_theme(app: QApplication, theme: str = 'light'):
        """Apply theme to entire application"""
        colors = ThemeManager.THEMES.get(theme, ThemeManager.THEMES['light'])
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['fg_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['fg_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['fg_primary']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['bg_primary']))
        
        app.setPalette(palette)
        
        # StyleSheet for enhanced control
        stylesheet = f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {colors['bg_primary']};
                color: {colors['fg_primary']};
            }}
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_dark']};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                border: 1px solid {colors['accent']};
                padding: 3px;
                border-radius: 3px;
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['accent']};
            }}
            QTabBar::tab {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                padding: 5px 15px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            QStatusBar {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
            }}
        """
        
        app.setStyleSheet(stylesheet)
    
    @staticmethod
    def get_color(theme: str, color_name: str) -> str:
        """Get specific color for theme"""
        return ThemeManager.THEMES[theme].get(color_name, '#000000')
```

---

### 3. Enhanced Status Bar

```python
# unlock_tool/gui/components/status_bar.py

from PyQt6.QtWidgets import QStatusBar, QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

class EnhancedStatusBar(QStatusBar):
    """Real-time operation status bar with indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize status bar components"""
        
        # Connection indicator (LED)
        self.connection_led = QLabel("●")
        self.connection_led.setStyleSheet("color: red; font-size: 14px;")
        self.addPermanentWidget(self.connection_led)
        
        # Status text
        self.status_text = QLabel("Ready")
        self.addPermanentWidget(self.status_text)
        
        # Operation queue badge
        self.queue_badge = QLabel("Queue: 0")
        self.queue_badge.setStyleSheet("""
            background-color: #FF6B6B;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
        """)
        self.addPermanentWidget(self.queue_badge)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(15)
        self.addPermanentWidget(self.progress_bar)
        
        # License info
        self.license_info = QLabel("License: Valid")
        self.addPermanentWidget(self.license_info)
    
    def set_connected(self, connected: bool, stable: bool = True):
        """Update connection indicator"""
        if connected:
            color = "green" if stable else "orange"
            tooltip = "Device connected" if stable else "Connection unstable"
        else:
            color = "red"
            tooltip = "Device disconnected"
        
        self.connection_led.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.connection_led.setToolTip(tooltip)
    
    def set_operation_status(self, operation: str, progress: int = 0):
        """Update operation status"""
        self.status_text.setText(f"Operation: {operation}")
        if progress > 0:
            self.progress_bar.setValue(progress)
        
        if progress == 100:
            self.progress_bar.setValue(0)
    
    def update_queue_count(self, count: int):
        """Update operation queue counter"""
        if count > 0:
            self.queue_badge.setText(f"Queue: {count}")
            self.queue_badge.setVisible(True)
        else:
            self.queue_badge.setVisible(False)
```

---

### 4. Operation Log Panel

```python
# unlock_tool/gui/components/operation_log.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from datetime import datetime

class OperationLogPanel(QWidget):
    """Displays timestamped operation history"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.max_entries = 1000
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(200)
        layout.addWidget(self.log_display)
        
        # Controls
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📥 Export")
        export_btn.clicked.connect(self.export_log)
        button_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def log_success(self, message: str):
        """Log successful operation"""
        self._add_log_entry(message, "success", "✅")
    
    def log_warning(self, message: str):
        """Log warning"""
        self._add_log_entry(message, "warning", "⚠️")
    
    def log_error(self, message: str):
        """Log error"""
        self._add_log_entry(message, "error", "❌")
    
    def log_info(self, message: str):
        """Log info"""
        self._add_log_entry(message, "info", "ℹ️")
    
    def _add_log_entry(self, message: str, level: str, icon: str):
        """Add timestamped log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color mapping
        colors = {
            'success': '#22C55E',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'info': '#3B82F6'
        }
        
        log_text = f"{icon} [{timestamp}] {message}"
        
        # Add to display
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(colors.get(level, '#000000')))
        
        cursor.insertText(log_text + "\n", fmt)
        self.log_display.setTextCursor(cursor)
        
        # Limit entries
        doc = self.log_display.document()
        if doc.blockCount() > self.max_entries:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
    
    def clear_log(self):
        """Clear all log entries"""
        self.log_display.clear()
    
    def export_log(self):
        """Export log to file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "", "Text Files (*.txt);;CSV Files (*.csv)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_display.toPlainText())
```

---

### 5. Integration in Main Window

```python
# Updated unlock_tool/gui/main_window_enhanced.py section

from gui.components.device_selector import AdvancedDeviceSelector
from gui.components.status_bar import EnhancedStatusBar
from gui.components.operation_log import OperationLogPanel
from gui.theme_manager import ThemeManager

class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eTool - Mobile Unlock Tool v2.1.0")
        self.resize(1400, 900)
        
        # Apply theme
        app = QApplication.instance()
        ThemeManager.apply_theme(app, 'light')  # or 'dark'
        
        # Setup UI components
        self.init_ui()
        self.init_status_bar()
    
    def init_status_bar(self):
        """Initialize enhanced status bar"""
        self.status_bar = EnhancedStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_connected(False)
    
    def init_ui(self):
        """Initialize main UI"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        
        # Left: Device Selector
        left_panel = QVBoxLayout()
        self.device_selector = AdvancedDeviceSelector(self.load_profiles())
        self.device_selector.device_selected.connect(self.on_device_selected)
        left_panel.addWidget(self.device_selector)
        
        # Center: Tabs
        center_panel = self.create_tabs()
        
        # Right: Operation Log
        self.operation_log = OperationLogPanel()
        
        # Splitters for resizable panels
        left_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_splitter.addWidget(QWidget())  # Device selector container
        left_splitter.addWidget(center_panel)
        left_splitter.addWidget(self.operation_log)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 2)
        left_splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(left_splitter)
```

---

## 🎯 Implementation Checklist

- [ ] Create `gui/components/` directory
- [ ] Add `device_selector.py` with AdvancedDeviceSelector
- [ ] Add `status_bar.py` with EnhancedStatusBar
- [ ] Add `operation_log.py` with OperationLogPanel
- [ ] Create `theme_manager.py` with dark/light themes
- [ ] Update `main_window_enhanced.py` to use new components
- [ ] Add theme toggle to menu bar
- [ ] Test all components individually
- [ ] Integration test with full application
- [ ] Update requirements.txt if new dependencies needed

---

## 📦 Files to Create/Modify

```
unlock_tool/gui/
├── components/
│   ├── __init__.py (new)
│   ├── device_selector.py (new)
│   ├── status_bar.py (new)
│   ├── operation_log.py (new)
│   └── dashboard.py (new - optional)
├── theme_manager.py (new)
├── main_window_enhanced.py (modify)
└── __init__.py (existing)
```

---

**Implementation Difficulty**: Medium  
**Estimated Time**: 2-3 weeks for all features  
**Testing Required**: Component + Integration tests
