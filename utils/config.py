import os
import json
import sys

class Config:
    CONFIG_FILE = "video_splitter_config.json"
    
    @staticmethod
    def get_base_path():
        """获取程序基础路径"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @classmethod
    def load(cls):
        """加载配置文件"""
        config_path = os.path.join(cls.get_base_path(), cls.CONFIG_FILE)
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    @classmethod
    def save(cls, config):
        """保存配置文件"""
        config_path = os.path.join(cls.get_base_path(), cls.CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump(config, f)
    
    @classmethod
    def get_ffmpeg_path(cls):
        """获取ffmpeg路径"""
        config = cls.load()
        default_path = os.path.join(cls.get_base_path(), "ffmpeg", "bin")
        return config.get('ffmpeg_path', default_path) 