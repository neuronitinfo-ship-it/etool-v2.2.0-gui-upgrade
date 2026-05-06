"""
Operation Log Panel - Displays timestamped operation history
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from datetime import datetime


class OperationLogPanel(QWidget):
    """Displays timestamped operation history with color-coded status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.max_entries = 1000
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QTextEdit()
        title.setReadOnly(True)
        title.setMaximumHeight(25)
        title.setText("Operation History")
        title.setStyleSheet("background: #f0f0f0; font-weight: bold; border: none;")
        layout.addWidget(title)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-family: Courier;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.log_display)
        
        # Controls
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📥 Export")
        export_btn.setMaximumWidth(100)
        export_btn.clicked.connect(self.export_log)
        button_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMaximumWidth(100)
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
        """Add timestamped log entry with color coding"""
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
        fmt.setFontWeight(500)
        
        cursor.insertText(log_text + "\n", fmt)
        self.log_display.setTextCursor(cursor)
        
        # Auto-scroll to latest entry
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
        
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
        
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Export Log", 
            "operation_log.txt",
            "Text Files (*.txt);;CSV Files (*.csv)"
        )
        
        if filename:
            content = self.log_display.toPlainText()
            
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                self.log_success(f"Log exported to {filename}")
            except Exception as e:
                self.log_error(f"Export failed: {str(e)}")
