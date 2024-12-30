import os
import shutil
import PyInstaller.__main__
import tkinterdnd2
import sys

# 获取tkdnd库路径
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

# 确保输出目录存在
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# 运行PyInstaller
PyInstaller.__main__.run([
    'main.py',
    '--name=视频分割工具',
    '--windowed',
    '--onedir',
    '--add-data=ffmpeg/bin;ffmpeg/bin',  # 将ffmpeg目录打包进去
    '--add-data=icon.ico;.',  # 添加图标文件
    '--icon=icon.ico',  # 设置exe图标
    '--noconfirm',
    '--clean',
    '--hidden-import=utils',
    '--hidden-import=gui',
    '--hidden-import=tkinterdnd2',
    '--collect-all=tkinterdnd2'  # 收集所有tkinterdnd2相关文件
])

# 创建配置文件
config = '''{
    "ffmpeg_path": "_internal/ffmpeg/bin"
}'''

# 写入配置文件
with open('dist/视频分割工具/video_splitter_config.json', 'w', encoding='utf-8') as f:
    f.write(config)

# 复制tkdnd文件夹，只复制Windows需要的文件
if os.path.exists(tkdnd_path):
    dst_path = os.path.join('dist', '视频分割工具', 'tkdnd')
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
        
        # 只复制Windows需要的文件
        windows_files = [
            'pkgIndex.tcl',
            'tkdnd.tcl',
            'tkdnd2.9.2.dll'  # Windows的动态链接库
        ]
        
        for file in windows_files:
            src_file = os.path.join(tkdnd_path, file)
            if os.path.exists(src_file):
                shutil.copy2(src_file, os.path.join(dst_path, file)) 