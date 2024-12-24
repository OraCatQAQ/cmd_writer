from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                           QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal

class EditorPanel(QWidget):
    content_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # 保存父窗口引用
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(600, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: #252526;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        
        self.title_label = QLabel("未打开文件")
        self.title_label.setStyleSheet("border: none;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E81123;
            }
        """)
        close_btn.clicked.connect(self.hide)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.editor.textChanged.connect(self._on_text_changed)
        
        layout.addWidget(title_bar)
        layout.addWidget(self.editor)
        
    def keyPressEvent(self, event):
        """处理按键事件"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)
    
    def _on_text_changed(self):
        self.content_changed.emit(self.editor.toPlainText())
        
    def set_content(self, title, content):
        self.title_label.setText(title)
        self.editor.setPlainText(content)
        
    def get_content(self):
        return self.editor.toPlainText() 