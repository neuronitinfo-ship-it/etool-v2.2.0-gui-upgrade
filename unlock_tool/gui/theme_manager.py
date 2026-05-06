"""
Theme Manager - Manages light and dark themes for the application
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Manages light and dark themes for PyQt6 application"""
    
    THEMES = {
        'light': {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F7FB',
            'fg_primary': '#1A1A1A',
            'fg_secondary': '#666666',
            'accent': '#1E6DFB',
            'accent_dark': '#0B4FD1',
            'accent_light': '#4A9EFF',
            'success': '#22C55E',
            'error': '#EF4444',
            'warning': '#F59E0B',
            'info': '#3B82F6',
        },
        'dark': {
            'bg_primary': '#1E1E1E',
            'bg_secondary': '#2D2D2D',
            'fg_primary': '#FFFFFF',
            'fg_secondary': '#CCCCCC',
            'accent': '#4A9EFF',
            'accent_dark': '#2E7FE6',
            'accent_light': '#6CB8FF',
            'success': '#4ADE80',
            'error': '#F87171',
            'warning': '#FBBF24',
            'info': '#60A5FA',
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
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['bg_secondary']))
        
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
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_dark']};
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_dark']};
                padding: 6px 9px;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                border: 1px solid {colors['accent']};
                padding: 3px;
                border-radius: 3px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {colors['accent_light']};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['accent']};
                background-color: {colors['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                padding: 5px 15px;
                border: 1px solid {colors['accent']};
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            QStatusBar {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                border-top: 1px solid {colors['accent']};
            }}
            QListWidget {{
                background-color: {colors['bg_secondary']};
                color: {colors['fg_primary']};
                border: 1px solid {colors['accent']};
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            QScrollBar:vertical {{
                background-color: {colors['bg_secondary']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['accent']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['accent_light']};
            }}
            QProgressBar {{
                background-color: {colors['bg_secondary']};
                border: 1px solid {colors['accent']};
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {colors['accent']};
                border-radius: 2px;
            }}
            QGroupBox {{
                color: {colors['fg_primary']};
                border: 1px solid {colors['accent']};
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            QCheckBox {{
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {colors['bg_secondary']};
                border: 1px solid {colors['accent']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['accent']};
                border: 1px solid {colors['accent']};
                border-radius: 3px;
            }}
        """
        
        app.setStyleSheet(stylesheet)
    
    @staticmethod
    def get_color(theme: str, color_name: str) -> str:
        """Get specific color for theme"""
        return ThemeManager.THEMES.get(theme, {}).get(color_name, '#000000')
