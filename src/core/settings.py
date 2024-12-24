from PyQt5.QtCore import QSettings
import os

class Settings:
    def __init__(self):
        self.settings = QSettings('FakeConsole', 'WindowSettings')

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