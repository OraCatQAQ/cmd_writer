import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QLineEdit, QShortcut, QLabel, QScrollArea, QFrame, QPushButton, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QTextCharFormat, QColor, QTextCursor, QKeySequence

from core.settings import Settings
from core.file_manager import FileManager
from threads.download_thread import DownloadThread
from ui.toolbar import ToolBar
from ui.styles import MAIN_WINDOW_STYLE, CONSOLE_STYLE, INPUT_LINE_STYLE

class FakeConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window)
        
        # 初始化核心组件
        self.settings = Settings()
        self.file_manager = FileManager(self.settings)
        
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
        
        # 创建并初始化工具栏和信息面板
        self.setupToolBar()
        self.setupInfoPanel()
        self.toolbar_widget.hide()
        self.info_panel.hide()
        
        # 初始状态下禁用输入
        self.input_line.setEnabled(False)
        self.input_line.setPlaceholderText("请先创建或打开文件 (Ctrl+N / Ctrl+O)")

    def initUI(self):
        # 设置窗口
        self.setWindowTitle('命令提示符')
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
        
        # 将 QLabel 替换为 QTextEdit
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(False)  # 允许编辑
        self.info_text.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: black;
                border: none;
                padding: 10px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        # 连接文本变化信号
        self.info_text.textChanged.connect(self.sync_content_to_main)
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
        shortcuts = [
            ('Ctrl+Q', self.close),
            ('Ctrl+M', self.showMinimized),
            ('Ctrl+H', self.showHelp),
            ('Ctrl+B', self.toggleToolBar),
            ('Ctrl+D', self.list_files),
            ('Ctrl+O', self.open_file),
            ('Ctrl+N', self.create_new_file),
            ('Ctrl+R', self.show_current_content),
        ]
        
        for key, callback in shortcuts:
            shortcut = QShortcut(key, self)
            shortcut.activated.connect(callback)
        
        # 添加关闭和重新打开信息面板的快捷键
        close_info_shortcut = QShortcut(QKeySequence('Esc'), self)
        close_info_shortcut.activated.connect(self.close_info_panel)
        
        reopen_info_shortcut = QShortcut(QKeySequence('Alt+Q'), self)
        reopen_info_shortcut.activated.connect(self.reopen_info_panel)

    def close_info_panel(self):
        """关闭信息面板并保存状态"""
        if self.info_panel.isVisible():
            self.last_info_state = {
                'title': self.info_title.text(),
                'content': self.info_text.toPlainText(),
                'readonly': self.info_text.isReadOnly()
            }
            self.info_panel.hide()

    def reopen_info_panel(self):
        """重新打开上次关闭的信息面板"""
        if hasattr(self, 'last_info_state') and self.last_info_state:
            self.info_text.setReadOnly(self.last_info_state['readonly'])
            self.show_info_panel(
                self.last_info_state['title'],
                self.last_info_state['content']
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toolbar_widget'):
            # 将工具栏放在右边
            self.toolbar_widget.setGeometry(
                self.width() - 40, 0, 40, self.height()
            )

    def update_download_info(self, text):
        if text.startswith('\r'):
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self._format_and_insert_text(text.lstrip('\r'))
        else:
            self._format_and_insert_text(text + '\n')
        
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def _format_and_insert_text(self, text):
        # 恢复原来的格式化逻辑
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
        if not hasattr(self.file_manager, 'current_file'):
            self._format_and_insert_text("[ERROR] 请先创建或打开文件\n")
            return
        
        text = self.input_line.text()
        if text:
            if hasattr(self, 'waiting_for_filename') and self.waiting_for_filename:
                success, filepath = self.file_manager.create_file(text)
                if success:
                    self._format_and_insert_text(f"[SUCCESS] 已创建新文件: {os.path.basename(filepath)}\n")
                    self.input_line.setEnabled(True)
                    self.input_line.setPlaceholderText("输入内容后按回车...")
                else:
                    self._format_and_insert_text(f"[WARNING] 文件已存在: {os.path.basename(filepath)}\n")
                self.waiting_for_filename = False
                
            elif hasattr(self, 'waiting_for_open') and self.waiting_for_open:
                if self.file_manager.open_file(text):
                    self._format_and_insert_text(f"[SUCCESS] 已切换到文件: {text}\n")
                    self.input_line.setEnabled(True)
                    self.input_line.setPlaceholderText("输入内容后按回车...")
                    # 打开文件后自动显示内容
                    self.show_current_content()
                else:
                    self._format_and_insert_text(f"[ERROR] 文件不存在: {text}\n")
                self.waiting_for_open = False
                
            else:
                self.file_manager.save_content(text)
                # 如果信息面板正在显示当前文件，更新其内容
                if self.info_panel.isVisible():
                    self.show_current_content()
            
            self.input_line.clear()

    def showHelp(self):
        help_text = """
[INFO] 快捷键帮助:
    Ctrl+Q : 退出程序
    Ctrl+M : 最小化窗口
    Ctrl+H : 显示帮助信息
    Ctrl+B : 显示/隐藏工具栏
    Ctrl+D : 显示文件列表
    Ctrl+O : 打开文件
    Ctrl+N : 新建文件
    Ctrl+R : 显示当前文件内容
    Esc   : 关闭信息窗口
    Alt+Q : 重新打开上次关闭的窗口
    
[INFO] 写作提示:
    - 所有输入内容会自动保存到当前文件
    - 每60秒自动保存一次
"""
        self._format_and_insert_text(help_text)

    def list_files(self):
        """显示小说目录下的所有文件"""
        files = self.file_manager.list_files()
        content = ""
        if not files:
            content = "目录为空"
        else:
            for file in files:
                content += (
                    f"{file['name']:<30} "
                    f"大小: {file['size']/1024:.1f} KB\n"
                    f"修改时间: {file['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
        
        # 对于文件列表，设置为只读
        self.info_text.setReadOnly(True)
        self.show_info_panel("文件列表", content)

    def create_new_file(self):
        self._format_and_insert_text("\n[INFO] 请输入新文件名 (不需要输入.txt后缀):")
        self.input_line.setEnabled(True)
        self.input_line.setPlaceholderText("输入文件名后按回车...")
        self.waiting_for_filename = True

    def open_file(self):
        self._format_and_insert_text("\n[INFO] 请输入要打开的文件名:")
        self.input_line.setEnabled(True)
        self.input_line.setPlaceholderText("输入文件名后按回车...")
        self.waiting_for_open = True

    def show_current_content(self):
        """显示当前文件内容"""
        try:
            with open(self.file_manager.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新信息面板标题和内容
            self.info_title.setText(f"文件内容 - {os.path.basename(self.file_manager.current_file)}")
            self.info_text.setPlainText(content)
            
            # 显示面板
            self.show_info_panel()
        except Exception as e:
            self._format_and_insert_text(f"[ERROR] 读取文件时出错: {str(e)}\n")

    def clearConsole(self):
        self.console.clear()

    def toggleToolBar(self):
        if self.toolbar_widget.isVisible():
            self.toolbar_widget.hide()
        else:
            self.toolbar_widget.show()

    def auto_save(self):
        if self.input_line.text():
            self.manual_save()

    def manual_save(self):
        text = self.input_line.text()
        if text:
            self.file_manager.save_content(text)
            self._format_and_insert_text(f"[SUCCESS] 内容已保存\n")

    def loadSettings(self):
        geometry = self.settings.load_geometry()
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.save_geometry(self.saveGeometry())
        self.auto_save_timer.stop()
        self.download_thread.running = False
        event.accept()

    def show_info_panel(self, title=None, content=None):
        """显示信息面板"""
        # 计算窗口位置（在工具栏左侧显示）
        x = self.width() - 440
        y = 50
        self.info_panel.move(x, y)
        
        if title:
            self.info_title.setText(title)
        if content:
            self.info_text.setPlainText(content)
        
        self.info_panel.show()

    def show_settings(self):
        current_dir = self.file_manager.novel_dir
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            current_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if new_dir:
            try:
                self.file_manager.update_novel_directory(new_dir)
                self._format_and_insert_text(f"[SUCCESS] 已更新保存目录: {new_dir}\n")
            except Exception as e:
                self._format_and_insert_text(f"[ERROR] 更新目录失败: {str(e)}\n")

    def sync_content_to_main(self):
        """将信息面板的内容同步到主窗口"""
        if hasattr(self, 'syncing') and self.syncing:
            return
        
        self.syncing = True
        try:
            current_file = self.file_manager.current_file
            content = self.info_text.toPlainText()
            
            # 保存到文件
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # 更新主窗口显示
            self._format_and_insert_text("[INFO] 内容已同步\n")
        finally:
            self.syncing = False
