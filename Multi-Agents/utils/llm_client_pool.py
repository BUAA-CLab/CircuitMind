# utils/llm_client_pool.py - 简化版LLM客户端池
"""简化的LLM客户端池化管理系统"""

import threading
import time
import hashlib
from typing import Dict, Optional
from openai import OpenAI
from dataclasses import dataclass
import logging

@dataclass
class ClientInfo:
    """客户端信息"""
    client: OpenAI
    created_at: float
    last_used: float
    usage_count: int = 0
    
    def is_expired(self, ttl: int = 3600) -> bool:
        """检查客户端是否过期"""
        return time.time() - self.created_at > ttl

class LLMClientPool:
    """简化的LLM客户端池"""
    
    def __init__(self, max_clients: int = 10, client_ttl: int = 3600):
        self.max_clients = max_clients
        self.client_ttl = client_ttl
        self._clients: Dict[str, ClientInfo] = {}
        self._lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def _generate_client_key(self, model_config) -> str:
        """生成客户端缓存键"""
        key_data = f"{model_config.base_url}:{model_config.api_key}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_client(self, model_config) -> OpenAI:
        """获取或创建LLM客户端"""
        if not model_config or not model_config.api_key:
            raise ValueError("Invalid model configuration: missing API key")
        
        client_key = self._generate_client_key(model_config)
        
        with self._lock:
            # 检查现有客户端
            if client_key in self._clients:
                client_info = self._clients[client_key]
                
                # 检查是否过期
                if not client_info.is_expired(self.client_ttl):
                    client_info.last_used = time.time()
                    client_info.usage_count += 1
                    return client_info.client
                else:
                    # 移除过期客户端
                    del self._clients[client_key]
            
            # 检查池大小限制
            if len(self._clients) >= self.max_clients:
                self._evict_least_used_client()
            
            # 创建新客户端
            try:
                client = OpenAI(
                    api_key=model_config.api_key,
                    base_url=model_config.base_url,
                    timeout=getattr(model_config, 'timeout', 30)
                )
                
                current_time = time.time()
                client_info = ClientInfo(
                    client=client,
                    created_at=current_time,
                    last_used=current_time,
                    usage_count=1
                )
                
                self._clients[client_key] = client_info
                return client
                
            except Exception as e:
                raise RuntimeError(f"Failed to create LLM client: {str(e)}")
    
    def _evict_least_used_client(self):
        """移除最少使用的客户端"""
        if not self._clients:
            return
        
        # 找到最少使用的客户端
        least_used_key = min(
            self._clients.keys(),
            key=lambda k: (self._clients[k].last_used, self._clients[k].usage_count)
        )
        
        del self._clients[least_used_key]
    
    def clear_all(self):
        """清空所有客户端"""
        with self._lock:
            self._clients.clear()
    
    def get_pool_stats(self) -> Dict[str, int]:
        """获取池统计信息"""
        with self._lock:
            return {
                "total_clients": len(self._clients),
                "max_clients": self.max_clients,
                "total_usage": sum(info.usage_count for info in self._clients.values())
            }

# 全局客户端池实例
_client_pool = LLMClientPool()

def get_llm_client_pool() -> LLMClientPool:
    """获取全局LLM客户端池"""
    return _client_pool