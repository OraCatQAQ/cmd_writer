from PyQt5.QtCore import QSettings
import os

class Settings:
    def __init__(self):
        self.settings = QSettings('FakeConsole', 'WindowSettings')
        self.default_shortcuts = {
            'close': 'Ctrl+Q',
            'minimize': 'Ctrl+M',
            'toggle_toolbar': 'Ctrl+B',
            'save': 'Ctrl+S',
            'show_content': 'Ctrl+R',
            'undo': 'Ctrl+Z',
            'close_editor': 'Esc'
        }

    def save_geometry(self, geometry):
        self.settings.setValue('geometry', geometry)

    def load_geometry(self):
        return self.settings.value('geometry')

    def save_novel_directory(self, path):
        self.settings.setValue('novel_directory', path)

    def load_novel_directory(self):
        default_path = os.path.join(os.path.expanduser('~'), 'novels')
        return self.settings.value('novel_directory', default_path)
        
    def save_show_status(self, show):
        self.settings.setValue('show_status', show)
        
    def load_show_status(self):
        return self.settings.value('show_status', True, type=bool)

    def save_shortcut(self, action, key):
        """保存快捷键设置"""
        self.settings.setValue(f'shortcuts/{action}', key)

    def load_shortcut(self, action):
        """加载快捷键设置"""
        return self.settings.value(f'shortcuts/{action}', self.default_shortcuts.get(action))

    def reset_shortcuts(self):
        """重置所有快捷键为默认值"""
        for action, key in self.default_shortcuts.items():
            self.save_shortcut(action, key) 