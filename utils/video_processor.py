import os
import math
import subprocess

class VideoProcessor:
    def __init__(self, ffmpeg_exe, ffprobe_exe):
        self.ffmpeg_exe = ffmpeg_exe
        self.ffprobe_exe = ffprobe_exe
    
    @staticmethod
    def get_file_size_gb(file_path):
        """获取文件大小（GB）"""
        return os.path.getsize(file_path) / (1024 * 1024 * 1024)
    
    def split_video(self, input_file, progress_callback=None, target_size=1.95, 
                   name_pattern="{name}-Cut#{num}", output_dir=None):
        """分割视频文件"""
        # 获取视频总时长（秒）
        duration = self._get_video_duration(input_file)
        
        file_size = self.get_file_size_gb(input_file)
        segments = math.ceil(file_size / target_size)
        segment_duration = duration / segments
        
        # 准备输出路径
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        for i in range(segments):
            if progress_callback:
                progress_callback(i, segments, f"正在处理：{base_name} - 第 {i+1}/{segments} 段")
            
            self._process_segment(input_file, i, segments, segment_duration, 
                                base_name, name_pattern, output_dir, progress_callback)
    
    def _get_video_duration(self, input_file):
        """获取视频时长"""
        cmd = f'"{self.ffprobe_exe}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
        try:
            return float(subprocess.check_output(cmd, shell=True).decode().strip())
        except subprocess.CalledProcessError as e:
            raise Exception(f"无法获取视频时长：{e}")
    
    def _process_segment(self, input_file, segment_index, total_segments, segment_duration,
                        base_name, name_pattern, output_dir, progress_callback):
        """处理单个分段"""
        start_time = segment_index * segment_duration
        output_name = name_pattern.format(name=base_name, num=segment_index+1) + ".mp4"
        
        if output_dir and output_dir != "与源文件相同":
            output_file = os.path.join(output_dir, output_name)
        else:
            output_file = os.path.join(os.path.dirname(input_file), output_name)
        
        cmd = self._build_ffmpeg_command(input_file, start_time, segment_duration, 
                                       output_file, segment_index == total_segments-1)
        
        self._run_ffmpeg_command(cmd, segment_duration, segment_index, 
                               total_segments, base_name, progress_callback)
    
    def _build_ffmpeg_command(self, input_file, start_time, segment_duration, output_file, is_last_segment):
        """构建ffmpeg命令"""
        if is_last_segment:
            return f'"{self.ffmpeg_exe}" -i "{input_file}" -ss {start_time} -c copy "{output_file}"'
        return f'"{self.ffmpeg_exe}" -i "{input_file}" -ss {start_time} -t {segment_duration} -c copy "{output_file}"'
    
    def _run_ffmpeg_command(self, cmd, segment_duration, segment_index, total_segments, 
                           base_name, progress_callback):
        """运行ffmpeg命令并处理进度"""
        try:
            process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
            
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                    
                if progress_callback and "time=" in line:
                    self._update_progress(line, segment_duration, segment_index, 
                                       total_segments, base_name, progress_callback)
            
            process.wait()
            if process.returncode != 0:
                raise Exception(f"ffmpeg返回错误代码：{process.returncode}")
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"视频分割失败：{e}")
    
    def _update_progress(self, line, segment_duration, segment_index, total_segments, 
                        base_name, progress_callback):
        """更新进度信息"""
        try:
            time_str = line.split("time=")[1].split()[0]
            current_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(time_str.split(":"))))
            segment_progress = current_time / segment_duration
            progress_callback(
                int((segment_index + segment_progress) / total_segments * 100),
                total_segments,
                f"正在处理：{base_name} - 第 {segment_index+1}/{total_segments} 段 ({int(segment_progress*100)}%)"
            )
        except:
            pass 