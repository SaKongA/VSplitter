import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from queue import Queue, Empty
from tkinterdnd2 import DND_FILES
from utils.config import Config
from utils.video_processor import VideoProcessor
from .widgets import (create_settings_frame, create_file_list, 
                     create_buttons, create_progress_display)

class VideoSplitterGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_dpi()
        self.init_variables()
        self.setup_widgets()
        self.setup_drag_drop()
        self.setup_ffmpeg()
        
    def setup_window(self):
        """设置窗口"""
        self.root.title("视频分割工具")
        
        # 设置窗口图标
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))
            ico_path = os.path.join(base_path, "icon.ico")
            
            if os.path.exists(ico_path):
                # 为Windows任务栏设置图标
                if sys.platform == 'win32':
                    try:
                        from ctypes import windll
                        myappid = 'mycompany.vsplitter.1.0'
                        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                        self.root.iconbitmap(ico_path)
                    except Exception as e:
                        print(f"设置任务栏图标失败: {e}")
        except Exception as e:
            print(f"加载图标失败: {e}")
        
    def setup_dpi(self):
        """设置DPI感知"""
        if sys.platform == 'win32':
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        # 设置默认字体
        default_font = ('Microsoft YaHei UI', 14)  # 使用微软雅黑UI字体
        self.root.option_add('*Font', default_font)
        
        # 设置ttk组件的字体
        style = ttk.Style()
        style.configure('TButton', font=default_font)
        style.configure('TLabel', font=default_font)
        style.configure('TLabelframe.Label', font=default_font)  # LabelFrame的标题
        style.configure('TEntry', font=default_font)
        
        # 调整窗口大小和缩放
        self.scale_factor = 1.2
        if sys.platform == 'win32':
            try:
                self.scale_factor = windll.shcore.GetScaleFactorForDevice(0) / 100
            except:
                pass
        
        width = int(1000 * self.scale_factor)
        height = int(600 * self.scale_factor)
        self.root.geometry(f"{width}x{height}")
    
    def init_variables(self):
        """初始化变量"""
        self.size_var = tk.StringVar(value="1.95")
        self.name_pattern_var = tk.StringVar(value="{name}-Cut#{num}")
        self.output_dir_var = tk.StringVar(value="与源文件相同")
        self.large_files = []
        
    def setup_widgets(self):
        """设置界面组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding=int(10 * self.scale_factor))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建设置面板
        callbacks = {
            'select_output_dir': self.select_output_dir,
            'reset_output_dir': self.reset_output_dir
        }
        create_settings_frame(self.main_frame, self.size_var, 
                            self.name_pattern_var, self.output_dir_var, 
                            callbacks, self.scale_factor)
        
        # 创建文件列表
        self.list_frame, self.file_listbox = create_file_list(self.main_frame, self.scale_factor)
        
        # 创建按钮
        button_callbacks = {
            'select_ffmpeg': self.select_ffmpeg_path,
            'import_files': self.import_files,
            'import_folder': self.import_folder,
            'remove_selected': self.remove_selected,
            'clear_files': self.clear_files,
            'select_all': self.select_all,
            'deselect_all': self.deselect_all,
            'process_selected': self.process_selected
        }
        create_buttons(self.main_frame, button_callbacks, self.scale_factor)
        
        # 创建进度显示
        progress_frame, self.progress_var, self.progress_bar, \
        self.total_progress_var, self.total_progress_bar = create_progress_display(self.main_frame, self.scale_factor)
    
    def setup_drag_drop(self):
        """设置拖放功能"""
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.handle_drop)
    
    def setup_ffmpeg(self):
        """设置ffmpeg"""
        if not self.check_ffmpeg():
            messagebox.showerror("错误", f"找不到ffmpeg！请确认ffmpeg已安装在：{Config.get_ffmpeg_path()}")
            self.root.quit()
        
        self.video_processor = VideoProcessor(
            os.path.join(Config.get_ffmpeg_path(), "ffmpeg.exe"),
            os.path.join(Config.get_ffmpeg_path(), "ffprobe.exe")
        )
    
    def check_ffmpeg(self):
        """检查ffmpeg是否可用"""
        ffmpeg_path = Config.get_ffmpeg_path()
        ffmpeg_exe = os.path.join(ffmpeg_path, "ffmpeg.exe")
        ffprobe_exe = os.path.join(ffmpeg_path, "ffprobe.exe")
        
        if not os.path.exists(ffmpeg_exe) or not os.path.exists(ffprobe_exe):
            if not hasattr(self, 'ffmpeg_error_shown'):
                self.ffmpeg_error_shown = True
                if messagebox.askyesno("错误", 
                    f"找不到ffmpeg！是否选择ffmpeg目录？\n\n"
                    f"当前路径：{ffmpeg_path}"):
                    self.select_ffmpeg_path()
            return False
        return True
    
    def select_ffmpeg_path(self):
        """选择ffmpeg目录"""
        path = filedialog.askdirectory(title="选择ffmpeg所在目录")
        if path:
            # 自动查找bin目录
            bin_path = path
            if not (os.path.exists(os.path.join(bin_path, "ffmpeg.exe")) and 
                    os.path.exists(os.path.join(bin_path, "ffprobe.exe"))):
                # 检查是否存在bin子目录
                possible_bin = os.path.join(path, "bin")
                if os.path.exists(possible_bin) and \
                   os.path.exists(os.path.join(possible_bin, "ffmpeg.exe")) and \
                   os.path.exists(os.path.join(possible_bin, "ffprobe.exe")):
                    bin_path = possible_bin
                else:
                    # 搜索子目录
                    found = False
                    for root, dirs, files in os.walk(path):
                        if "ffmpeg.exe" in files and "ffprobe.exe" in files:
                            bin_path = root
                            found = True
                            break
                    if not found:
                        messagebox.showerror("错误", "在选择的目录中未找到ffmpeg！")
                        return
            
            # 保存配置
            config = Config.load()
            config['ffmpeg_path'] = bin_path
            Config.save(config)
            
            # 重新初始化视频处理器
            self.video_processor = VideoProcessor(
                os.path.join(bin_path, "ffmpeg.exe"),
                os.path.join(bin_path, "ffprobe.exe")
            )
            
            messagebox.showinfo("成功", "已成功设置ffmpeg路径！")
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def reset_output_dir(self):
        """重置输出目录为默认"""
        self.output_dir_var.set("与源文件相同")
    
    def import_files(self):
        """导入文件"""
        files = filedialog.askopenfilenames(
            title="选择视频文件",
            filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        )
        if files:
            self.process_dropped_files(files)
    
    def import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            self.process_dropped_files([folder])
    
    def handle_drop(self, event):
        """处理文件拖放"""
        files = self.root.tk.splitlist(event.data)
        self.process_dropped_files(files)
    
    def process_dropped_files(self, files):
        """处理拖入的文件和文件夹"""
        new_files = []
        ignored_files = []
        processed_paths = set()
        
        for file_path in files:
            if os.path.isdir(file_path):
                # 处理文件夹
                for root, _, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        if full_path.lower().endswith('.mp4'):
                            self.process_single_file(full_path, new_files, ignored_files, processed_paths)
            else:
                # 处理单个文件
                if file_path.lower().endswith('.mp4'):
                    self.process_single_file(file_path, new_files, ignored_files, processed_paths)
                else:
                    ignored_files.append(file_path)
        
        # 更新列表
        if new_files:
            for file in new_files:
                if file not in self.large_files:
                    self.large_files.append(file)
                    self.file_listbox.insert(tk.END, file)
        
        # 显示导入结果
        message = []
        if new_files:
            message.append(f"成功导入 {len(new_files)} 个文件")
        if ignored_files:
            message.append(f"忽略 {len(ignored_files)} 个文件")
        
        if message:
            messagebox.showinfo("导入结果", "\n".join(message))
    
    def process_single_file(self, file_path, new_files, ignored_files, processed_paths):
        """处理单个文件"""
        if file_path in processed_paths:
            return
        
        processed_paths.add(file_path)
        try:
            if self.video_processor.get_file_size_gb(file_path) > float(self.size_var.get()):
                new_files.append(file_path)
            else:
                ignored_files.append(file_path)
        except:
            ignored_files.append(file_path)
    
    def remove_selected(self):
        """删除选中的文件"""
        selected = self.file_listbox.curselection()
        if not selected:
            return
        
        # 从后往前删除，避免索引变化
        for index in reversed(selected):
            self.file_listbox.delete(index)
            self.large_files.pop(index)
    
    def clear_files(self):
        """清空文件列表"""
        self.file_listbox.delete(0, tk.END)
        self.large_files.clear()
    
    def select_all(self):
        """全选"""
        self.file_listbox.select_set(0, tk.END)
    
    def deselect_all(self):
        """取消全选"""
        self.file_listbox.selection_clear(0, tk.END)
    
    def process_selected(self):
        """处理选中的文件"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请选择要处理的文件！")
            return
        
        selected_files = [self.large_files[i] for i in selected_indices]
        
        # 禁用所有按钮
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, ttk.Button):
                        btn['state'] = 'disabled'
        
        # 创建处理线程
        self.processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(selected_files,),
            daemon=True
        )
        self.processing_thread.start()
        
        # 启动进度更新检查
        self.root.after(100, self.check_progress)
    
    def process_files_thread(self, selected_files):
        """在单独的线程中处理文件"""
        try:
            target_size = float(self.size_var.get())
        except ValueError:
            self.update_gui(error="目标文件大小必须是有效的数字！", complete=True)
            return
        
        if target_size <= 0:
            self.update_gui(error="目标文件大小必须大于0！", complete=True)
            return
        
        name_pattern = self.name_pattern_var.get()
        output_dir = self.output_dir_var.get()
        
        total_files = len(selected_files)
        
        try:
            for i, file in enumerate(selected_files, 1):
                self.update_gui(
                    total_progress=(i - 1) / total_files * 100,
                    total_message=f"{i-1}/{total_files}",
                    progress=0,
                    message=f"{os.path.basename(file)}"
                )
                
                try:
                    self.video_processor.split_video(
                        file, 
                        progress_callback=self.update_progress,
                        target_size=target_size,
                        name_pattern=name_pattern,
                        output_dir=output_dir
                    )
                except Exception as e:
                    self.update_gui(error=f"处理文件 {file} 时出错：{str(e)}")
                    continue
                
                self.update_gui(
                    total_progress=(i / total_files * 100),
                    total_message=f"{i}/{total_files}"
                )
            
            self.update_gui(
                total_progress=100,
                total_message=f"{total_files}/{total_files}",
                message="处理完成！",
                complete=True
            )
        except Exception as e:
            self.update_gui(
                error=f"发生错误：{str(e)}",
                complete=True
            )
    
    def update_gui(self, progress=None, message=None, error=None, complete=False, 
                   total_progress=None, total_message=None):
        """将GUI更新操作放入队列"""
        if not hasattr(self, 'gui_queue'):
            self.gui_queue = Queue()
        self.gui_queue.put({
            'progress': progress,
            'message': message,
            'error': error,
            'complete': complete,
            'total_progress': total_progress,
            'total_message': total_message
        })
    
    def check_progress(self):
        """检查并应用GUI更新"""
        try:
            while True:
                if not hasattr(self, 'gui_queue'):
                    break
                
                update = self.gui_queue.get_nowait()
                
                if update.get('progress') is not None:
                    self.progress_bar['value'] = update['progress']
                
                if update.get('message'):
                    self.progress_var.set(update['message'])
                
                if update.get('total_progress') is not None:
                    self.total_progress_bar['value'] = update['total_progress']
                
                if update.get('total_message'):
                    self.total_progress_var.set(update['total_message'])
                
                if update.get('error'):
                    messagebox.showerror("错误", update['error'])
                
                if update.get('complete'):
                    # 重新启用所有按钮
                    for widget in self.main_frame.winfo_children():
                        if isinstance(widget, ttk.Frame):
                            for btn in widget.winfo_children():
                                if isinstance(btn, ttk.Button):
                                    btn['state'] = 'normal'
                    if not update.get('error'):
                        messagebox.showinfo("完成", "所有选中的文件处理完成！")
                    return
                
        except Empty:
            pass
        
        if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
            self.root.after(100, self.check_progress)
    
    def update_progress(self, current, total, message):
        """更新处理进度"""
        self.update_gui(
            progress=(current / total) * 100,
            message=message
        )