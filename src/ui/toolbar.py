from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        from ui.styles import TOOLBAR_STYLE
        self.setFixedWidth(40)
        self.setStyleSheet(TOOLBAR_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        self.buttons = []
        layout.addStretch()

    def add_button(self, text, tooltip, callback):
        btn = QPushButton(text)
        btn.setFixedSize(36, 36)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        self.layout().insertWidget(len(self.buttons), btn)
        self.buttons.append(btn) 