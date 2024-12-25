import os
import shutil
import subprocess
from datetime import datetime

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
def create_resources():
    """确保资源目录存在"""
    if not os.path.exists('resources'):
        os.makedirs('resources')

def build_executable():
    """构建可执行文件"""
    try:
        # 使用 PyInstaller 构建
        subprocess.run(['pyinstaller', 'build_config.spec'], check=True)
        
        # 创建发布目录
        release_dir = f'release/cmd_writer_v1.0_{datetime.now().strftime("%Y%m%d")}'
        if not os.path.exists(release_dir):
            os.makedirs(release_dir)    
        
        # 复制构建文件到发布目录
        shutil.copy('dist/cmd_writer.exe', release_dir)
        
        # 创建必要的文档
        with open(f'{release_dir}/使用说明.txt', 'w', encoding='utf-8') as f:
            f.write("""cmd_writer使用说明

1. 快捷键：
   - Ctrl+B : 显示/隐藏工具栏
   - Ctrl+R : 显示当前文件内容
   - Ctrl+M : 最小化
   - Ctrl+Q : 退出
   - Esc : 关闭内容小窗进行沉浸式摸鱼
   
2. 使用说明 
    打开工具栏，点击设置，设置文件目录
    开始摸鱼

""")
        
        print(f"构建成功！发布文件位于: {release_dir}")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {str(e)}")
        
def main():
    clean_build_dirs()
    create_resources()
    build_executable()

if __name__ == '__main__':
    main() 