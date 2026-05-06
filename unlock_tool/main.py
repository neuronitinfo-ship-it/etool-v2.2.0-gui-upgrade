import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window_enhanced import EnhancedMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnhancedMainWindow()
    window.show()
    sys.exit(app.exec())