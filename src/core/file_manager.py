import os
from datetime import datetime

class FileManager:
    def __init__(self, settings):
        self.settings = settings
        self.novel_dir = self.settings.load_novel_directory()
        self.ensure_novel_directory()
        self.current_file = None

    def ensure_novel_directory(self):
        if not os.path.exists(self.novel_dir):
            os.makedirs(self.novel_dir)

#    def create_default_file(self):
#        filename = f"我的小说_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
#        return os.path.join(self.novel_dir, filename)

    def list_files(self):
        files = []
        for file in os.listdir(self.novel_dir):
            file_path = os.path.join(self.novel_dir, file)
            size = os.path.getsize(file_path)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            files.append({
                'name': file,
                'size': size,
                'modified': modified_time
            })
        return files

    def create_file(self, filename):
        if not filename.endswith('.txt'):
            filename += '.txt'
        file_path = os.path.join(self.novel_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                pass
            self.current_file = file_path
            return True, file_path
        return False, file_path

    def open_file(self, filename):
        if not filename.endswith('.txt'):
            filename += '.txt'
        file_path = os.path.join(self.novel_dir, filename)
        if os.path.exists(file_path):
            self.current_file = file_path
            return True
        return False

    def save_content(self, content):
        """保存内容到文件"""
        if self.current_file is None:
            raise ValueError("No file is currently open")
        try:
            with open(self.current_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{content}\n")  
            return True
        except Exception as e:
            raise Exception(f"保存失败: {str(e)}")

    def update_novel_directory(self, new_path):
        self.novel_dir = new_path
        self.settings.save_novel_directory(new_path)
        self.ensure_novel_directory()#        self.current_file = self.create_default_file()
