import os
import sys
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from gui.main_window import VideoSplitterGUI

def main():
    # 设置tkdnd路径
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        base_path = os.path.dirname(sys.executable)
        os.environ['TKDND_LIBRARY'] = os.path.join(base_path, 'tkdnd')
    
    root = TkinterDnD.Tk()
    
    # 设置图标
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(ico_path):
            root.iconbitmap(ico_path)
    except Exception as e:
        print(f"设置图标失败: {e}")
    
    app = VideoSplitterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 