# src/config/monitor.py
import time
import threading
from pathlib import Path
from typing import Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix in ['.yaml', '.yml', '.json']:
            # 防止重复触发
            current_time = time.time()
            if file_path in self.last_modified:
                if current_time - self.last_modified[file_path] < 1: # 1秒内的重复修改事件忽略
                    return
            
            self.last_modified[file_path] = current_time
            self.callback(file_path)

class ConfigMonitor:
    """配置文件监控器"""
    
    def __init__(self, config_dir: str, callback: Callable):
        self.config_dir = Path(config_dir)
        self.callback = callback
        # Watchdog 依赖检查
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("Warning: watchdog library not installed. Config monitoring will not be available.")
            print("Please install it using: pip install watchdog")
            self.observer = None
            return

        self.observer = Observer()
        self.handler = ConfigFileHandler(self._on_config_changed)
    
    def start(self):
        """开始监控"""
        if not self.observer:
            return
        self.observer.schedule(self.handler, str(self.config_dir), recursive=True)
        self.observer.start()
        print(f"Config monitor started for directory: {self.config_dir}")
    
    def stop(self):
        """停止监控"""
        if not self.observer:
            return
        self.observer.stop()
        self.observer.join()
        print("Config monitor stopped.")
    
    def _on_config_changed(self, file_path: Path):
        """配置文件变更回调"""
        print(f"Configuration file changed: {file_path}")
        self.callback(file_path)
