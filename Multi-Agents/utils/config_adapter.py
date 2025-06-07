"""
新配置适配器 - 完全基于新配置系统
"""

from typing import List, Dict, Any
from src.config import get_config_manager

class ConfigAdapter:
    """配置适配器 - 提供旧API兼容性"""
    
    def __init__(self):
        self.config_manager = get_config_manager()
    
    @property
    def config(self):
        return self.config_manager.config
    
    @property
    def MODEL_NAME(self) -> str:
        return self.config.current_model
    
    @MODEL_NAME.setter
    def MODEL_NAME(self, value: str):
        self.config_manager.switch_model(value)
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.config_manager.get_model_config().api_key
    
    @property
    def OPENAI_BASE_URL(self) -> str:
        return self.config_manager.get_model_config().base_url
    
    @property
    def MAX_RETRY_ATTEMPTS(self) -> int:
        return self.config_manager.get_agent_config("CoderAgent").max_retry_attempts
    
    @property
    def MAX_AUTO_FIX_ATTEMPTS(self) -> int:
        return self.config_manager.get_agent_config("CoderAgent").max_auto_fix_attempts
    
    @property
    def RAG_ONE(self) -> bool:
        return self.config.rag.enabled
    
    @property
    def RAG_TWO(self) -> bool:
        return self.config.rag.enabled
    
    @property
    def EXPERIMENTS_ROOT(self) -> str:
        return self.config.experiments.root_dir
    
    @property
    def TARGET_EXPERIMENTS(self) -> List[str]:
        return self.config.experiments.target_experiments
    
    @property
    def AGENT_SYSTEM_MESSAGES(self) -> Dict[str, str]:
        return self.config.agent_system_messages
    
    @property
    def SUMMARY_JSON_PATH(self) -> str:
        """动态生成摘要JSON路径"""
        model_name = self.config.current_model
        return f"./knowledge_base/Model-incrementment/{model_name}.json"
    
    def get_api_keys_base_url(self, model_name: str):
        """获取API密钥和Base URL"""
        model_config = self.config_manager.get_model_config(model_name)
        return model_config.api_config.api_keys, model_config.api_config.base_url
    
    def update_config(self, model_name: str, key_index: int):
        """更新配置"""
        self.config_manager.switch_model(model_name)
        model_config = self.config_manager.get_model_config(model_name)
        if 0 <= key_index < len(model_config.api_config.api_keys):
            model_config.api_config.current_key_index = key_index
    
    def get_experiment_output_root(self) -> str:
        """获取实验输出根目录"""
        return self.config.experiments.get_output_dir(self.config.current_model)

# 创建全局实例
_adapter = ConfigAdapter()

# 导出兼容属性
MODEL_NAME = _adapter.MODEL_NAME
OPENAI_API_KEY = _adapter.OPENAI_API_KEY
OPENAI_BASE_URL = _adapter.OPENAI_BASE_URL
MAX_RETRY_ATTEMPTS = _adapter.MAX_RETRY_ATTEMPTS
MAX_AUTO_FIX_ATTEMPTS = _adapter.MAX_AUTO_FIX_ATTEMPTS
RAG_ONE = _adapter.RAG_ONE
RAG_TWO = _adapter.RAG_TWO
EXPERIMENTS_ROOT = _adapter.EXPERIMENTS_ROOT
TARGET_EXPERIMENTS = _adapter.TARGET_EXPERIMENTS
AGENT_SYSTEM_MESSAGES = _adapter.AGENT_SYSTEM_MESSAGES

# 兼容函数
def get_api_keys_base_url(model_name: str):
    return _adapter.get_api_keys_base_url(model_name)

def update_config(model_name: str, key_index: int):
    return _adapter.update_config(model_name, key_index)

def get_experiment_output_root() -> str:
    return _adapter.get_experiment_output_root()