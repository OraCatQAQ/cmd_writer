from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                           QTreeView, QFileSystemModel, QVBoxLayout,
                           QMenu, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QDir
import os

class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border: none;
            }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: none;
                padding: 8px;
                margin: 2px;
                text-align: left;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QTreeView {
                background-color: #252526;
                border: none;
                color: #ffffff;
                font-family: 'Consolas', monospace;
            }
            QTreeView::item:hover {
                background-color: #2A2D2E;
            }
            QTreeView::item:selected {
                background-color: #094771;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 添加按钮组
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        
        self.buttons = []
        self.add_button("📁 新建文件", "创建新文件 (Ctrl+N)", self.parent.create_new_file, button_layout)
        self.add_button("💾 保存", "保存当前文件 (Ctrl+S)", self.parent.save_current_file, button_layout)
        self.add_button("⚙️ 设置", "设置保存目录", self.parent.show_settings, button_layout)
        
        # 添加文件树
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setNameFilters(['*.txt'])
        self.file_model.setNameFilterDisables(False)
        
        self.file_tree.setModel(self.file_model)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setColumnHidden(1, True)
        self.file_tree.setColumnHidden(2, True)
        self.file_tree.setColumnHidden(3, True)
        
        # 连接文件树的双击和右键菜单信号
        self.file_tree.doubleClicked.connect(self._on_file_double_clicked)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self._show_context_menu)
        
        # 将按钮组和文件树添加到主布局
        layout.addWidget(button_widget)
        layout.addWidget(self.file_tree)
        
        # 初始化文件树根目录
        if hasattr(self.parent, 'file_manager'):
            self.set_root_path(self.parent.file_manager.novel_dir)
        
    def add_button(self, text, tooltip, callback, layout):
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        self.buttons.append(btn)
        
    def set_root_path(self, path):
        """设置文件树的根目录"""
        if os.path.exists(path):
            self.file_model.setRootPath(path)
            self.file_tree.setRootIndex(self.file_model.index(path))
        
    def _on_file_double_clicked(self, index):
        """处理文件双击事件"""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            filename = os.path.basename(file_path)
            if self.parent.file_manager.open_file(filename):
                self.parent._format_and_insert_text(f"[SUCCESS] 已切换到文件: {filename}\n")
                self.parent.input_line.setEnabled(True)
                self.parent.input_line.setPlaceholderText("输入内容后按回车...")
                # 打开文件后自动显示内容
                self.parent.show_current_content()

    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        
        # 添加新建文件选项
        new_file_action = menu.addAction("新建文件")
        new_file_action.triggered.connect(self._create_new_file)
        
        # 获取当前选中的项
        index = self.file_tree.indexAt(position)
        if index.isValid():
            file_path = self.file_model.filePath(index)
            if os.path.isfile(file_path):
                # 添加删除文件选项
                delete_action = menu.addAction("删除文件")
                delete_action.triggered.connect(lambda: self._delete_file(file_path))
        
        menu.exec_(self.file_tree.viewport().mapToGlobal(position))

    def _create_new_file(self):
        """创建新文件"""
        filename, ok = QInputDialog.getText(
            self, '新建文件', '请输入文件名:',
            text='新文件.txt'
        )
        
        if ok and filename:
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            success, filepath = self.parent.file_manager.create_file(filename)
            if success:
                self.parent._format_and_insert_text(f"[SUCCESS] 已创建新文件: {filename}\n")
                # 自动打开新创建的文件
                self.parent.file_manager.open_file(filename)
                self.parent.show_current_content()
                self.parent.input_line.setEnabled(True)
                self.parent.input_line.setPlaceholderText("输入内容后按回车...")
            else:
                self.parent._format_and_insert_text(f"[WARNING] 文件已存在: {filename}\n")

    def _delete_file(self, file_path):
        """删除文件"""
        filename = os.path.basename(file_path)
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除文件 {filename} 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                self.parent._format_and_insert_text(f"[SUCCESS] 已删除文件: {filename}\n")
                # 如果删除的是当前打开的文件，清除当前文件
                if self.parent.file_manager.current_file == file_path:
                    self.parent.file_manager.current_file = None
                    self.parent.input_line.setEnabled(False)
                    self.parent.input_line.setPlaceholderText("请先创建或打开文件")
                    self.parent.editor_panel.hide()
            except Exception as e:
                self.parent._format_and_insert_text(f"[ERROR] 删除文件失败: {str(e)}\n")