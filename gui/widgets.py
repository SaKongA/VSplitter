import tkinter as tk
from tkinter import ttk
import sys

def get_padding():
    """获取基于DPI的padding值"""
    if sys.platform == 'win32':
        try:
            from ctypes import windll
            return int(16 * (windll.shcore.GetScaleFactorForDevice(0) / 100))
        except:
            pass
    return 16

def create_settings_frame(parent, size_var, name_pattern_var, output_dir_var, callbacks, scale_factor=1):
    """创建设置面板"""
    frame = ttk.LabelFrame(parent, text="设置", padding=str(int(8 * scale_factor)))
    frame.pack(fill=tk.X, pady=int(8 * scale_factor))
    
    # 分割大小设置
    size_frame = ttk.Frame(frame)
    size_frame.pack(fill=tk.X, pady=int(4 * scale_factor))
    ttk.Label(size_frame, text="目标文件大小(GB):").pack(side=tk.LEFT)
    size_entry = ttk.Entry(size_frame, textvariable=size_var, width=12)
    size_entry.pack(side=tk.LEFT, padx=int(8 * scale_factor))
    
    # 文件命名规则
    name_frame = ttk.Frame(frame)
    name_frame.pack(fill=tk.X, pady=int(2 * scale_factor))
    ttk.Label(name_frame, text="命名规则:").pack(side=tk.LEFT)
    name_entry = ttk.Entry(name_frame, textvariable=name_pattern_var)
    name_entry.pack(side=tk.LEFT, padx=int(5 * scale_factor), fill=tk.X, expand=True)
    ttk.Label(name_frame, text=".mp4").pack(side=tk.LEFT)
    
    # 输出目录
    output_frame = ttk.Frame(frame)
    output_frame.pack(fill=tk.X, pady=int(2 * scale_factor))
    ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT)
    ttk.Label(output_frame, textvariable=output_dir_var).pack(side=tk.LEFT, padx=int(5 * scale_factor))
    ttk.Button(output_frame, text="选择", command=callbacks['select_output_dir']).pack(side=tk.LEFT)
    ttk.Button(output_frame, text="重置", command=callbacks['reset_output_dir']).pack(side=tk.LEFT, padx=int(5 * scale_factor))
    
    return frame

def create_file_list(parent, scale_factor=1):
    """创建文件列表"""
    frame = ttk.LabelFrame(parent, text="待处理文件", padding=str(int(8 * scale_factor)))
    frame.pack(fill=tk.BOTH, expand=True, pady=int(8 * scale_factor))
    
    # 创建列表和滚动条
    listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=12)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    # 放置列表和滚动条
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    return frame, listbox

def create_buttons(parent, callbacks, scale_factor=1):
    """创建按钮"""
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.X, pady=int(8 * scale_factor))
    
    padding = int(8 * scale_factor)
    
    left_frame = ttk.Frame(frame)
    left_frame.pack(side=tk.LEFT)
    
    right_frame = ttk.Frame(frame)
    right_frame.pack(side=tk.RIGHT)
    
    # 左侧按钮
    ttk.Button(left_frame, text="设置ffmpeg", 
               command=callbacks['select_ffmpeg'],
               width=10).pack(side=tk.LEFT, padx=padding)
    ttk.Button(left_frame, text="导入文件",
               command=callbacks['import_files']).pack(side=tk.LEFT, padx=padding)
    ttk.Button(left_frame, text="导入文件夹",
               command=callbacks['import_folder']).pack(side=tk.LEFT, padx=padding)
    ttk.Button(left_frame, text="删除选中",
               command=callbacks['remove_selected']).pack(side=tk.LEFT, padx=padding)
    ttk.Button(left_frame, text="清空列表",
               command=callbacks['clear_files']).pack(side=tk.LEFT, padx=padding)
    
    # 右侧按钮
    ttk.Button(right_frame, text="全选",
               command=callbacks['select_all']).pack(side=tk.LEFT, padx=padding)
    ttk.Button(right_frame, text="取消全选",
               command=callbacks['deselect_all']).pack(side=tk.LEFT, padx=padding)
    ttk.Button(right_frame, text="开始处理",
               command=callbacks['process_selected']).pack(side=tk.LEFT, padx=padding)
    
    return frame

def create_progress_display(parent, scale_factor=1):
    """创建进度显示"""
    padding = int(8 * scale_factor)
    
    frame = ttk.LabelFrame(parent, text="处理进度", padding=str(padding))
    frame.pack(fill=tk.X, pady=padding)
    
    # 总进度
    total_frame = ttk.Frame(frame)
    total_frame.pack(fill=tk.X, pady=int(2 * scale_factor))
    ttk.Label(total_frame, text="总进度：").pack(side=tk.LEFT)
    total_progress_var = tk.StringVar(value="0/0")
    ttk.Label(total_frame, textvariable=total_progress_var).pack(side=tk.RIGHT)
    total_progress_bar = ttk.Progressbar(frame, mode='determinate')
    total_progress_bar.pack(fill=tk.X, pady=(0, padding))
    
    # 当前文件进度
    current_frame = ttk.Frame(frame)
    current_frame.pack(fill=tk.X, pady=int(2 * scale_factor))
    ttk.Label(current_frame, text="当前文件：").pack(side=tk.LEFT)
    progress_var = tk.StringVar(value="就绪")
    ttk.Label(current_frame, textvariable=progress_var).pack(side=tk.LEFT, padx=(padding, 0))
    progress_bar = ttk.Progressbar(frame, mode='determinate')
    progress_bar.pack(fill=tk.X, pady=(0, padding))
    
    return frame, progress_var, progress_bar, total_progress_var, total_progress_bar 