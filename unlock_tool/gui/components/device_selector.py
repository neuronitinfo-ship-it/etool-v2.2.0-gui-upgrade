"""
Advanced Device Selector - Enhanced device selection with search and filters
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class AdvancedDeviceSelector(QWidget):
    """Enhanced device selection with search, filters, and favorites"""
    
    device_selected = pyqtSignal(dict)
    
    def __init__(self, profiles):
        super().__init__()
        self.profiles = profiles if profiles else []
        self.favorites = set()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
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
        
        self.filter_brand.setMaximumWidth(100)
        self.filter_security.setMaximumWidth(100)
        self.filter_chipset.setMaximumWidth(100)
        
        filter_layout.addWidget(self.filter_brand)
        filter_layout.addWidget(self.filter_security)
        filter_layout.addWidget(self.filter_chipset)
        filter_layout.addWidget(self.show_favorites)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Device list
        self.device_list = QListWidget()
        self.device_list.itemDoubleClicked.connect(self.on_device_selected)
        self.device_list.itemClicked.connect(self.on_device_clicked)
        layout.addWidget(self.device_list)
        
        # Favorite toggle button
        self.toggle_fav_btn = QPushButton("⭐ Add to Favorites")
        self.toggle_fav_btn.clicked.connect(self.toggle_current_favorite)
        layout.addWidget(self.toggle_fav_btn)
        
        self.setLayout(layout)
        self.populate_devices()
    
    def populate_devices(self):
        """Load all devices into list"""
        self.device_list.clear()
        # Handle both dict format (keys are codenames) and list format
        devices = self.profiles.values() if isinstance(self.profiles, dict) else self.profiles
        for device in devices:
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
    
    def toggle_current_favorite(self):
        """Add/remove current device from favorites"""
        current_item = self.device_list.currentItem()
        if current_item:
            device = current_item.data(Qt.ItemDataRole.UserRole)
            self.toggle_favorite(device)
            self.on_device_clicked(current_item)
    
    def toggle_favorite(self, device):
        """Add/remove device from favorites"""
        key = f"{device['brand']}-{device['model']}"
        if key in self.favorites:
            self.favorites.remove(key)
        else:
            self.favorites.add(key)
    
    def on_device_clicked(self, item):
        """Update favorite button text when device is clicked"""
        device = item.data(Qt.ItemDataRole.UserRole)
        key = f"{device['brand']}-{device['model']}"
        
        if key in self.favorites:
            self.toggle_fav_btn.setText("⭐ Remove from Favorites")
        else:
            self.toggle_fav_btn.setText("⭐ Add to Favorites")
    
    def on_device_selected(self, item):
        """Emit signal when device selected"""
        device = item.data(Qt.ItemDataRole.UserRole)
        self.device_selected.emit(device)
