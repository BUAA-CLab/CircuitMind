# src/config/config_manager.py
from typing import Optional, Dict, Any, List
import os
import logging
from pathlib import Path
from .models import AppConfig, ModelConfig, AgentConfig
from .loaders import ConfigLoader
from .validators import ConfigValidator
from .cache import ConfigCache

class ConfigManager:
    """配置管理器 - 单例模式"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_dir: str = "configs"):
        if self._config is not None: # Check if already initialized
            # If using cache, ensure it's initialized or re-initialized as needed
            if not hasattr(self, '_cache'):
                self._cache = ConfigCache()
            return
        
        self.loader = ConfigLoader(config_dir)
        self.validator = ConfigValidator()
        self._cache = ConfigCache() # Initialize the cache attribute
        self._config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """加载完整配置"""
        try:
            # 1. 加载基础配置
            base_config = self.loader.load_base_config()
            
            # 2. 加载环境配置
            resolved_env_name = os.getenv("ENVIRONMENT", "development") 
            env_config = self.loader.load_environment_config(resolved_env_name)
            
            # 3. 加载模型配置
            models = self.loader.load_models_config()
            
            # 4. 合并配置
            merged_config = self._merge_configs(base_config, env_config)
            
            # 5. 构建AppConfig
            app_config = self._build_app_config(merged_config, models, current_env_name=resolved_env_name) 
            
            # 6. 验证当前模型设置
            if app_config.current_model not in app_config.models and app_config.models:
                first_model = list(app_config.models.keys())[0]
                print(f"Warning: Model '{app_config.current_model}' not found, using '{first_model}'")
                app_config.current_model = first_model
            
            # 7. 验证配置
            if app_config.models:
                # print(f"Loaded {len(app_config.models)} models: {list(app_config.models.keys())[:5]}...")
                self.validator.validate(app_config)
            else:
                print("Warning: No models configured")
            
            return app_config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Creating fallback configuration...")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> AppConfig:
        """创建回退配置"""
        from .models import RAGConfig, ExperimentConfig, LoggingConfig
        
        return AppConfig(
            debug=False,
            environment="development",
            current_model="qwen2.5-coder:14b",
            models={},
            agents={},
            rag=RAGConfig(),
            experiments=ExperimentConfig(),
            logging=LoggingConfig(),
            agent_system_messages={}
        )
    
    def _merge_configs(self, base: Dict[str, Any], env: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        merged = base.copy()
        for key, value in env.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        return merged
    
    def _build_app_config(self, config_data: Dict[str, Any], models: Dict[str, ModelConfig], current_env_name: str) -> AppConfig:
        from .models import RAGConfig, ExperimentConfig, LoggingConfig
        
        # 优先使用配置文件中定义的 "environment" 键（如果存在）
        # 否则，使用从 os.getenv 解析出的环境名称
        effective_environment = config_data.get("environment", current_env_name)
        
        return AppConfig(
            debug=config_data.get("debug", False),
            environment=effective_environment, # <--- 使用修正后的环境名称
            current_model=config_data.get("current_model", "qwen2.5-coder:14b"),
            models=models,
            agents={
                name: AgentConfig(**{k: v for k, v in agent_config.items() if k != 'output_format'})
                for name, agent_config in config_data.get("agents", {}).items()
            },
            rag=RAGConfig(**config_data.get("rag", {})),
            experiments=ExperimentConfig(**config_data.get("experiments", {})),
            logging=LoggingConfig(**config_data.get("logging", {})),
            agent_system_messages=config_data.get("agent_system_messages", {})
        )
    
    @classmethod
    def get_instance(cls, config_dir: str = "configs") -> 'ConfigManager':
        """获取配置管理器实例"""
        """获取配置管理器实例"""
        # Ensures that current_model (potentially updated by switch_model)
        # is not reset by an automatic reload_config() on subsequent get_instance() calls.
        # Reloading should be an explicit action by the client if config files change on disk.
        if cls._instance is None:
            cls._instance = cls(config_dir)
        # else: # This block containing reload_config() was removed.
            # cls._instance.reload_config() 
        return cls._instance
    
    @property
    def config(self) -> AppConfig:
        """获取应用配置"""
        return self._config
    
    def get_model_config(self, model_name: Optional[str] = None) -> ModelConfig:
        """获取模型配置"""
        model_name = model_name or self._config.current_model
        if model_name not in self._config.models:
            # 如果模型不存在，尝试创建一个基本配置
            print(f"Warning: Model {model_name} not found in configuration")
            from .models import APIConfig
            return ModelConfig(
                name=model_name,
                api_config=APIConfig(api_keys=[""], base_url="")
            )
        return self._config.models[model_name]
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """获取智能体配置"""
        return self._config.get_agent_config(agent_name)
    
    def switch_model(self, model_name: str):
        """切换模型"""
        if model_name in self._config.models:
            self._config.switch_model(model_name)
            # 2. 调用内部方法来刷新 ConfigManager 层面上的兼容性属性
            self._set_compatibility_attributes() 
        else:
            print(f"Warning: Model {model_name} not found, keeping current model")
    def _set_compatibility_attributes(self):
        """
        内部方法：根据当前的 self._config.current_model
        设置 ConfigManager 实例上的兼容性属性 (OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME)。
        这样外部可以直接通过 cm.OPENAI_API_KEY 访问。
        """
        current_model_config = self.get_model_config(self._config.current_model)
        
        # 将这些兼容性属性直接设置到 ConfigManager 实例上
        # 这样 main.py 中的 config.OPENAI_API_KEY 就可以直接变成 config_manager.OPENAI_API_KEY
        # 或者，如果 main.py 仍然需要 AppConfig 实例上这些属性，那么就设置到 _config 上
        # 这里我选择设置到 ConfigManager 实例上，因为 ConfigManager 是单例且是核心
        self.OPENAI_API_KEY = current_model_config.api_key
        self.OPENAI_BASE_URL = current_model_config.base_url
        self.MODEL_NAME = current_model_config.name # 将模型名称也同步过来

        logging.debug(f"Compatibility attributes set: Model={self.MODEL_NAME}, URL={self.OPENAI_BASE_URL}, API_KEY={self.OPENAI_API_KEY[:10]}...")

    def reload_config(self):
        """重新加载配置"""
        self._config = self._load_config()
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get_api_key(self, model_name: Optional[str] = None) -> str:
        """获取API密钥（兼容现有代码）"""
        model_config = self.get_model_config(model_name)
        return model_config.api_key
    
    def get_base_url(self, model_name: Optional[str] = None) -> str:
        """获取Base URL（兼容现有代码）"""
        model_config = self.get_model_config(model_name)
        return model_config.base_url
    
    def get_api_keys_list(self, model_name: Optional[str] = None) -> List[str]:
        """获取API密钥列表（兼容现有代码）"""
        model_config = self.get_model_config(model_name)
        return model_config.api_config.api_keys