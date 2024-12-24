import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QLineEdit, QShortcut, QLabel, QScrollArea, QFrame, QPushButton, QHBoxLayout, QFileDialog, QTextBrowser, QDialog, QGroupBox, QDialogButtonBox, QCheckBox, QTabWidget, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QTextCharFormat, QColor, QTextCursor, QKeySequence

from core.settings import Settings
from core.file_manager import FileManager
from threads.download_thread import DownloadThread
from ui.toolbar import ToolBar
from ui.styles import MAIN_WINDOW_STYLE, CONSOLE_STYLE, INPUT_LINE_STYLE
from ui.editor_panel import EditorPanel

class FakeConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window)
        
        # 初始化撤销栈
        self.undo_stack = []
        self.max_undo_steps = 50  # 最大撤销步数
        
        # 初始化核心组件
        self.settings = Settings()
        self.file_manager = FileManager(self.settings)
        
        # 添加行编辑相关的属性
        self.current_line_number = -1  # 当前编辑的行号，-1表示新行
        self.file_lines = []  # 文件的所有行
        
        self.initUI()
        self.loadSettings()
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(r'C:\Windows\System32\cmd.exe'))
        
        # 设置自动保存
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)  # 每60秒自动保存
        
        # 启动假下载线程
        self.download_thread = DownloadThread()
        self.download_thread.update_signal.connect(self.update_download_info)
        self.download_thread.start()
        
        # 创建并初始化工具栏和编辑器面板
        self.toolbar_widget = ToolBar(self)
        self.editor_panel = EditorPanel(self)
        self.editor_panel.content_changed.connect(self.on_editor_content_changed)
        
        # 设置工具栏位置
        self.toolbar_widget.move(0, 0)
        self.toolbar_widget.show()
        
        # 设置编辑器面板位置
        self.editor_panel.hide()
        
        # 初始状态下禁用输入
        self.input_line.setEnabled(False)
        self.input_line.setPlaceholderText("请先创建或打开文件")

    def initUI(self):
        # 设置窗口
        self.setWindowTitle('C:\Windows\System32\cmd.exe')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建控制台显示区域
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(CONSOLE_STYLE)
        layout.addWidget(self.console)
        
        # 创建状态信息显示区域
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: #00ff00;
                font-family: 'Consolas';
                font-size: 14px;
                padding: 5px 10px;
                border-top: 1px solid #333;
                border-bottom: 1px solid #333;
            }
        """)
        layout.addWidget(self.status_label)
        self.status_label.setVisible(self.settings.load_show_status())
        
        # 创建输入区域
        self.input_line = QLineEdit()
        self.input_line.setStyleSheet(INPUT_LINE_STYLE)
        self.input_line.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_line)
        
        # 设置窗口样式
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # 设置快捷键
        self.setupShortcuts()
        
        # 修改输入框提示文本
        self.input_line.setPlaceholderText("按 Ctrl+H 查看帮助信息")

    def setupToolBar(self):
        self.toolbar_widget = ToolBar(self)
        
        # 添加工具按钮
        buttons = [
            ('📁', '查看文件列表 (Ctrl+D)', self.list_files),
            ('📝', '新建文件 (Ctrl+N)', self.create_new_file),
            ('📂', '打开文件 (Ctrl+O)', self.open_file),
            ('📄', '显示当前内容 (Ctrl+R)', self.show_current_content),
            ('⚙️', '设置 ', self.show_settings),
            ('❌', '关闭 (Ctrl+Q)', self.close),
        ]
        
        for text, tooltip, callback in buttons:
            self.toolbar_widget.add_button(text, tooltip, callback)

    def setupInfoPanel(self):
        # 创建信息窗口
        self.info_panel = QWidget(self)
        self.info_panel.setFixedSize(400, 500)
        
        # 创建布局
        layout = QVBoxLayout(self.info_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: black;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        
        self.info_title = QLabel("文件信息")
        self.info_title.setStyleSheet("color: white;")
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c42b1c;
            }
        """)
        close_btn.clicked.connect(self.info_panel.hide)
        
        title_layout.addWidget(self.info_title)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #404040;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: black;")
        content_layout = QVBoxLayout(content_widget)
        
        # 使用 QTextBrowser 替代 QTextEdit
        self.info_text = QTextBrowser()
        self.info_text.setOpenExternalLinks(False)  # 禁止打开外部链接
        self.info_text.setStyleSheet("""
            QTextBrowser {
                color: white;
                background-color: black;
                border: none;
                padding: 10px;
                font-family: Consolas, Monaco, monospace;
            }
            QTextBrowser a {
                color: #00aaff;
                text-decoration: none;
            }
            QTextBrowser a:hover {
                color: #55ccff;
                text-decoration: underline;
            }
        """)
        
        # 连接链接点击信号
        self.info_text.anchorClicked.connect(self._handle_file_click)
        content_layout.addWidget(self.info_text)
        
        # 将内容部件设置到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 组装布局
        layout.addWidget(title_bar)
        layout.addWidget(scroll_area)
        
        # 设置窗口样式
        self.info_panel.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 1px solid #333;
            }
        """)
        self.info_panel.hide()

    def setupShortcuts(self):
        """设置快捷键"""
        # 清除现有的快捷键
        if hasattr(self, '_shortcuts'):
            for shortcut in self._shortcuts:
                shortcut.setEnabled(False)
                shortcut.deleteLater()
        
        self._shortcuts = []
        
        # 设置新的快捷键
        shortcuts = [
            ('close', self.close),
            ('minimize', self.showMinimized),
            ('toggle_toolbar', self.toggleToolBar),
            ('save', self.manual_save),
            ('show_content', self.show_current_content),
            ('undo', self.undo_last_input),
            ('close_editor', self.close_editor_panel)
        ]
        
        for action, callback in shortcuts:
            key = self.settings.load_shortcut(action)
            if key:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(callback)
                self._shortcuts.append(shortcut)

    def close_info_panel(self):
        """关闭编辑器面板"""
        if self.editor_panel.isVisible():
            self.last_editor_state = {
                'title': self.editor_panel.title_label.text(),
                'content': self.editor_panel.get_content()
            }
            self.editor_panel.hide()

    def reopen_info_panel(self):
        """重新打开编辑器面板"""
        if hasattr(self, 'last_editor_state') and self.last_editor_state:
            self.editor_panel.set_content(
                self.last_editor_state['title'],
                self.last_editor_state['content']
            )
            self.editor_panel.show()
            # 调整编辑器面板位置
            self.editor_panel.move(
                self.width() - self.editor_panel.width() - 10,
                50
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toolbar_widget'):
            # 将工具栏放在左边，并且高度与窗口一致
            self.toolbar_widget.setGeometry(
                0, 0, 250, self.height()
            )
            # 调整编辑器面板位置
            if hasattr(self, 'editor_panel'):
                self.editor_panel.move(
                    self.width() - self.editor_panel.width() - 10,
                    50
                )

    def update_download_info(self, text):
        """处理下载信息的显示"""
        if text.startswith('\r'):
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self._insert_download_text(text.lstrip('\r'))
        else:
            self._insert_download_text(text + '\n')
        
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def _insert_download_text(self, text):
        """在控制台插入下载相关的文本"""
        cursor = self.console.textCursor()
        format = QTextCharFormat()
        
        if '[ERROR]' in text:
            format.setForeground(QColor('#ff5555'))
        elif '[WARNING]' in text:
            format.setForeground(QColor('#ffb86c'))
        elif '[SUCCESS]' in text:
            format.setForeground(QColor('#50fa7b'))
        elif '[INFO]' in text:
            format.setForeground(QColor('#8be9fd'))
        else:
            format.setForeground(QColor('#f8f8f2'))
            
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text, format)

    def _format_and_insert_text(self, text):
        """处理文件操作相关的信息显示"""
        # 如果是文件操作相关的信息（包含特定标记），且状态栏被禁用，则不显示
        if any(tag in text for tag in ['[ERROR]', '[WARNING]', '[SUCCESS]', '[INFO]']):
            if not self.settings.load_show_status():
                return  # 直接返回，不显示任何信息
            
            # 添加时间戳并显示在状态栏
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_text = f"[{timestamp}] {text}"
            self.status_label.setText(formatted_text.strip())
        else:
            # 其他类型的信息（如下载信息）正常显示在控制台
            cursor = self.console.textCursor()
            format = QTextCharFormat()
            
            if '[ERROR]' in text:
                format.setForeground(QColor('#ff5555'))
            elif '[WARNING]' in text:
                format.setForeground(QColor('#ffb86c'))
            elif '[SUCCESS]' in text:
                format.setForeground(QColor('#50fa7b'))
            elif '[INFO]' in text:
                format.setForeground(QColor('#8be9fd'))
            else:
                format.setForeground(QColor('#f8f8f2'))
            
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text, format)

    def process_input(self):
        """处理回车输入"""
        if not self.file_manager.current_file:
            self._format_and_insert_text("[ERROR] 请先创建或打开文件")
            return
            
        # 保存当前行
        self.save_current_line()
        
        # 清空输入框
        self.input_line.clear()
        
        # 移动到下一行
        if self.current_line_number >= 0:
            self.move_to_line(self.current_line_number + 1)

    def update_file_content(self, text):
        """更新文件内容"""
        try:
            # 读取当前文件内容
            with open(self.file_manager.current_file, 'r', encoding='utf-8') as f:
                self.file_lines = f.read().splitlines()
            
            # 更新或插入内容
            if self.current_line_number >= 0:
                # 修改现有行
                if self.current_line_number < len(self.file_lines):
                    if text:  # 有内容则更新
                        self.file_lines[self.current_line_number] = text
                    else:  # 空内容则删除该行
                        self.file_lines.pop(self.current_line_number)
            else:
                # 添加新行
                if text:
                    self.file_lines.append(text)
            
            # 保存回文件
            with open(self.file_manager.current_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.file_lines))
                if self.file_lines:  # 确保最后有换行符
                    f.write('\n')
                    
        except Exception as e:
            raise Exception(f"更新文件内容失败: {str(e)}")
    
    def move_to_line(self, line_number):
        """移动到指定行"""
        try:
            with open(self.file_manager.current_file, 'r', encoding='utf-8') as f:
                self.file_lines = f.read().splitlines()
            
            # 如果是最后一行之后，切换到新行模式
            if line_number >= len(self.file_lines):
                self.current_line_number = -1
                self.input_line.clear()
                self.input_line.setPlaceholderText("输入新内容...")
                return
            
            # 如果是有效行号，显示该行内容
            if line_number >= 0 and line_number < len(self.file_lines):
                self.current_line_number = line_number
                self.input_line.setText(self.file_lines[line_number])
                self.input_line.setPlaceholderText(f"正在编辑第 {line_number + 1} 行...")
                
        except Exception as e:
            self._format_and_insert_text(f"[ERROR] 移动到指定行失败: {str(e)}")
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if not self.file_manager.current_file:
            super().keyPressEvent(event)
            return
            
        if event.key() == Qt.Key_Up:
            # 先保存当前行的修改
            self.save_current_line()
            # 向上移动一行
            if self.current_line_number == -1:
                # 如果当前在新行模式，移动到最后一行
                self.move_to_line(len(self.file_lines) - 1)
            else:
                # 否则移动到上一行
                self.move_to_line(max(0, self.current_line_number - 1))
                
        elif event.key() == Qt.Key_Down:
            # 先保存当前行的修改
            self.save_current_line()
            # 向下移动一行
            if self.current_line_number == -1:
                # 如果当前在新行模式，保持在新行
                return
            # 移动到下一行或新行模式
            self.move_to_line(self.current_line_number + 1)
            
        elif event.key() == Qt.Key_Delete and self.current_line_number >= 0:
            # 删除当前行
            self.save_for_undo()
            self.update_file_content("")  # 传入空字符串表示删除
            self.move_to_line(self.current_line_number)  # 保持在当前位置
            
        else:
            super().keyPressEvent(event)

    def save_current_line(self):
        """保存当前行的修改"""
        if not self.file_manager.current_file:
            return
        
        text = self.input_line.text().strip()
        if text or self.current_line_number >= 0:  # 允许空行修改
            try:
                # 保存当前状态用于撤销
                self.save_for_undo()
                
                # 更新文件内容
                self.update_file_content(text)
                
                self._format_and_insert_text("[SUCCESS] 内容已保存")
                
                # 更新编辑器面板内容
                if self.editor_panel.isVisible():
                    self.show_current_content()
                    
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] {str(e)}")

    def showHelp(self):
        help_text = """
[INFO] 快捷键帮助:
    Ctrl+Q : 退出程序
    Ctrl+M : 最小化窗口
    Ctrl+H : 显示帮助信息
    Ctrl+B : 显示/隐藏工具栏
    Ctrl+S : 保存当前内容
    Ctrl+R : 显示当前文件内容
    Ctrl+Z : 撤销上一次输入
    Esc   : 关闭编辑器窗口
    
[INFO] 使用说明:
    - 在文件树中右键可以新建或删除文件
    - 双击文件可以打开
    - 所有输入内容会自动保存
    - 每60秒自动保存一次
"""
        self._format_and_insert_text(help_text)

    def show_current_content(self):
        """显示当前文件内容"""
        try:
            if not self.file_manager.current_file:
                return
            
            with open(self.file_manager.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新编辑器面板内容
            self.editor_panel.set_content(
                f"文件内容 - {os.path.basename(self.file_manager.current_file)}", 
                content
            )
            self.editor_panel.show()
            
            # 调整编辑器面板位置
            self.editor_panel.move(
                self.width() - self.editor_panel.width() - 10,
                50
            )
            
        except Exception as e:
            self._format_and_insert_text(f"[ERROR] 读取文件时出错: {str(e)}")

    def clearConsole(self):
        self.console.clear()

    def toggleToolBar(self):
        if self.toolbar_widget.isVisible():
            self.toolbar_widget.hide()
        else:
            self.toolbar_widget.show()

    def auto_save(self):
        """自动保存功能"""
        if self.file_manager.current_file and self.input_line.text():
            try:
                text = self.input_line.text()
                if self.file_manager.save_content(text):
                    self._format_and_insert_text(f"[SUCCESS] 内容已自动保存")
                    # 如果编辑器面板正在显示当前文件，更新其内容
                    if self.editor_panel.isVisible():
                        self.show_current_content()
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 自动保存失败: {str(e)}")

    def manual_save(self):
        """手动保存功能"""
        if not self.file_manager.current_file:
            return
        
        text = self.input_line.text()
        if text:
            try:
                self.file_manager.save_content(text)
                self._format_and_insert_text(f"[SUCCESS] 内容已保存")
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 保存失败: {str(e)}")

    def loadSettings(self):
        geometry = self.settings.load_geometry()
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.save_geometry(self.saveGeometry())
        self.auto_save_timer.stop()
        self.download_thread.running = False
        event.accept()

    def show_settings(self):
        """显示设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 基本设置选项卡
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # 目录设置
        dir_group = QGroupBox("文件保存目录")
        dir_layout = QHBoxLayout()
        dir_label = QLineEdit(self.file_manager.novel_dir)
        dir_label.setReadOnly(True)
        dir_button = QPushButton("选择目录")
        
        def choose_dir():
            new_dir = QFileDialog.getExistingDirectory(
                self, "选择保存目录", self.file_manager.novel_dir,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
            if new_dir:
                dir_label.setText(new_dir)
        
        dir_button.clicked.connect(choose_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(dir_button)
        dir_group.setLayout(dir_layout)
        
        # 状态显示设置
        status_check = QCheckBox("显示状态信息")
        status_check.setChecked(self.settings.load_show_status())
        
        basic_layout.addWidget(dir_group)
        basic_layout.addWidget(status_check)
        
        # 快捷键设置选项卡
        shortcut_tab = QWidget()
        shortcut_layout = QVBoxLayout(shortcut_tab)
        
        shortcut_group = QGroupBox("快捷键设置")
        grid_layout = QGridLayout()
        
        shortcut_editors = {}
        row = 0
        
        for action, description in {
            'close': '退出程序',
            'minimize': '最小化窗口',
            'toggle_toolbar': '显示/隐藏工具栏',
            'save': '保存内容',
            'show_content': '显示文件内容',
            'undo': '撤销操作',
            'close_editor': '关闭编辑器'
        }.items():
            # 添加描述标签
            grid_layout.addWidget(QLabel(description), row, 0)
            
            # 添加快捷键编辑框
            editor = QLineEdit(self.settings.load_shortcut(action))
            editor.setPlaceholderText("点击输入快捷键")
            
            def create_key_press_handler(editor, action):
                def handle_key_press(event):
                    key_sequence = []
                    if event.modifiers() & Qt.ControlModifier:
                        key_sequence.append('Ctrl')
                    if event.modifiers() & Qt.AltModifier:
                        key_sequence.append('Alt')
                    if event.modifiers() & Qt.ShiftModifier:
                        key_sequence.append('Shift')
                    
                    key = event.key()
                    if key != Qt.Key_Control and key != Qt.Key_Alt and key != Qt.Key_Shift:
                        key_sequence.append(QKeySequence(key).toString())
                    
                    if key_sequence:
                        editor.setText('+'.join(key_sequence))
                    event.accept()
                return handle_key_press
            
            editor.keyPressEvent = create_key_press_handler(editor, action)
            shortcut_editors[action] = editor
            grid_layout.addWidget(editor, row, 1)
            
            row += 1
        
        # 添加重置按钮
        reset_btn = QPushButton("重置为默认")
        def reset_shortcuts():
            self.settings.reset_shortcuts()
            for action, editor in shortcut_editors.items():
                editor.setText(self.settings.load_shortcut(action))
        reset_btn.clicked.connect(reset_shortcuts)
        
        shortcut_group.setLayout(grid_layout)
        shortcut_layout.addWidget(shortcut_group)
        shortcut_layout.addWidget(reset_btn)
        
        # 添加选项卡
        tab_widget.addTab(basic_tab, "基本设置")
        tab_widget.addTab(shortcut_tab, "快捷键设置")
        layout.addWidget(tab_widget)
        
        # 确定取消按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, dialog
        )
        
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # 保存基本设置
            new_dir = dir_label.text()
            if new_dir != self.file_manager.novel_dir:
                try:
                    self.file_manager.update_novel_directory(new_dir)
                    self.toolbar_widget.set_root_path(new_dir)
                    self._format_and_insert_text(f"[SUCCESS] 已更新保存目录: {new_dir}\n")
                except Exception as e:
                    self._format_and_insert_text(f"[ERROR] 更新目录失败: {str(e)}\n")
            
            # 保存状态显示设置
            show_status = status_check.isChecked()
            self.settings.save_show_status(show_status)
            self.status_label.setVisible(show_status)
            
            # 保存快捷键设置
            for action, editor in shortcut_editors.items():
                new_shortcut = editor.text()
                if new_shortcut:
                    self.settings.save_shortcut(action, new_shortcut)
            
            # 更新快捷键
            self.setupShortcuts()

    def sync_content_to_main(self):
        """将信息面板的内容同步到主窗口"""
        if hasattr(self, 'syncing') and self.syncing:
            return
        
        self.syncing = True
        try:
            if self.file_manager.current_file is None:
                self._format_and_insert_text("[ERROR] 请先创建或打开文件\n")
                return
            
            current_file = self.file_manager.current_file
            content = self.info_text.toPlainText()
            
            # 保存到文件
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # 更新主窗口显示
            self._format_and_insert_text("[INFO] 内容已同步\n")
        except Exception as e:
            self._format_and_insert_text(f"[ERROR] 同步失败: {str(e)}\n")
        finally:
            self.syncing = False

    def save_current_file(self):
        """保存当前文件"""
        if self.file_manager.current_file:
            content = self.editor_panel.get_content()
            try:
                with open(self.file_manager.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._format_and_insert_text("[SUCCESS] 文件已保存\n")
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 保存失败: {str(e)}\n")

    def on_editor_content_changed(self):
        """处理编辑器内容变化"""
        if not hasattr(self, '_is_updating_editor'):
            self._is_updating_editor = False
        
        if not self._is_updating_editor and self.file_manager.current_file:
            try:
                # 保存当前状态用于撤销
                self.save_for_undo()
                
                # 保存编辑器内容
                content = self.editor_panel.get_content()
                with open(self.file_manager.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 保存失败: {str(e)}")

    def save_for_undo(self):
        """保存当前文件状态用于撤销"""
        if self.file_manager.current_file:
            try:
                # 读取当前文件内容
                try:
                    with open(self.file_manager.current_file, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                except:
                    current_content = ""
                
                # 将当前状态保存到撤销栈
                self.undo_stack.append(current_content)
                # 限制撤销栈大小
                if len(self.undo_stack) > self.max_undo_steps:
                    self.undo_stack.pop(0)
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 保存撤销状态失败: {str(e)}")

    def undo_last_input(self):
        """撤销上一次操作"""
        if not self.undo_stack:
            self._format_and_insert_text("[WARNING] 没有可撤销的操作")
            return
            
        try:
            if self.file_manager.current_file:
                # 获取上一个状态
                previous_content = self.undo_stack.pop()
                
                # 恢复文件内容
                with open(self.file_manager.current_file, 'w', encoding='utf-8') as f:
                    f.write(previous_content)
                
                self._format_and_insert_text("[SUCCESS] 已撤销上一次操作")
                
                # 如果编辑器面板打开，更新显示
                if self.editor_panel.isVisible():
                    self._is_updating_editor = True
                    try:
                        self.show_current_content()
                    finally:
                        self._is_updating_editor = False
        except Exception as e:
            self._format_and_insert_text(f"[ERROR] 撤销失败: {str(e)}")

    def close_editor_panel(self):
        """关闭编辑器面板"""
        if hasattr(self, 'editor_panel') and self.editor_panel.isVisible():
            # 保存当前编辑器内容
            if self.file_manager.current_file:
                content = self.editor_panel.get_content()
                try:
                    # 保存当前状态用于撤销
                    self.save_for_undo()
                    
                    # 保存编辑器内容
                    with open(self.file_manager.current_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self._format_and_insert_text("[SUCCESS] 内容已保存")
                except Exception as e:
                    self._format_and_insert_text(f"[ERROR] 保存失败: {str(e)}")
            
            # 隐藏编辑器面板
            self.editor_panel.hide()
