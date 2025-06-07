# src/config/validators.py
from typing import List, Any
from .models import AppConfig, ModelConfig

class ConfigValidationError(Exception):
    """配置验证错误"""
    pass

class ConfigValidator:
    """配置验证器"""
    
    def validate(self, config: AppConfig) -> None:
        """验证配置"""
        errors = []
        
        # 验证模型配置
        errors.extend(self._validate_models(config.models))
        
        # 验证当前模型
        if config.current_model and config.current_model not in config.models:
            errors.append(f"Current model '{config.current_model}' not found in models")
        
        # 验证路径
        errors.extend(self._validate_paths(config))
        
        if errors:
            raise ConfigValidationError("Configuration validation failed:\n" + "\n".join(errors))
    
    def _validate_models(self, models: dict) -> List[str]:
        """验证模型配置"""
        errors = []
        
        if not models:
            # 模型配置为空时给出警告而不是错误，因为可能在初始化阶段
            print("Warning: No models configured")
            return errors
        
        for name, model in models.items():
            if not model.api_config.api_keys:
                errors.append(f"Model '{name}' has no API keys")
            
            if not model.api_config.base_url:
                errors.append(f"Model '{name}' has no base URL")
            
            # 验证API密钥格式
            for key in model.api_config.api_keys:
                if not isinstance(key, str) or not key.strip():
                    errors.append(f"Model '{name}' has invalid API key format")
        
        return errors
    
    def _validate_paths(self, config: AppConfig) -> List[str]:
        """验证路径配置"""
        errors = []
        
        # 验证实验根目录
        if config.experiments.root_dir:
            from pathlib import Path
            root_path = Path(config.experiments.root_dir)
            if not root_path.exists():
                # 对于不存在的路径，给出警告而不是错误
                print(f"Warning: Experiment root directory does not exist: {config.experiments.root_dir}")
        
        # 验证知识库路径
        if config.rag.enabled:
            from pathlib import Path
            kb_path = Path(config.rag.knowledge_base_path)
            if not kb_path.exists():
                print(f"Warning: Knowledge base directory does not exist: {config.rag.knowledge_base_path}")
        
        return errors