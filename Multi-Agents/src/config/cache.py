# src/config/cache.py
from typing import Dict, Any, Optional
import time
from functools import wraps

class ConfigCache:
    """配置缓存"""
    
    def __init__(self, ttl: int = 300):  # 5分钟TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            data, timestamp = self.cache[key]["data"], self.cache[key]["timestamp"]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        self.cache[key] = {
            "data": value,
            "timestamp": time.time()
        }
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()

def cached_config(cache_key: str):
    """配置缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, '_cache'):
                cached_result = self._cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            result = func(self, *args, **kwargs)
            
            if hasattr(self, '_cache'):
                self._cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator
