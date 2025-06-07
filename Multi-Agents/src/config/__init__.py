# src/config/__init__.py
"""
配置管理模块

这个模块提供统一的配置管理功能，支持：
- 多环境配置
- 模型配置管理
- 智能体配置
- 实验配置
- 配置验证
"""

from .config_manager import ConfigManager
from .models import (
    AppConfig, 
    ModelConfig, 
    APIConfig, 
    AgentConfig, 
    RAGConfig, 
    ExperimentConfig, 
    LoggingConfig
)
from .loaders import ConfigLoader
from .validators import ConfigValidator, ConfigValidationError

__all__ = [
    'ConfigManager',
    'AppConfig',
    'ModelConfig', 
    'APIConfig',
    'AgentConfig',
    'RAGConfig',
    'ExperimentConfig',
    'LoggingConfig',
    'ConfigLoader',
    'ConfigValidator',
    'ConfigValidationError'
]

# 提供便捷的访问方式
def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return ConfigManager.get_instance()

def get_current_config() -> AppConfig:
    """获取当前应用配置"""
    return get_config_manager().config