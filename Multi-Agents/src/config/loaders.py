# src/config/loaders.py
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Union
import os
from .models import AppConfig, ModelConfig, APIConfig, AgentConfig, RAGConfig, ExperimentConfig, LoggingConfig

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(exist_ok=True)
        (self.config_dir / "models").mkdir(exist_ok=True)
        (self.config_dir / "environments").mkdir(exist_ok=True)
        (self.config_dir / "experiments").mkdir(exist_ok=True)
    
    def load_yaml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载YAML文件"""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.config_dir / path
        
        if not path.exists():
            print(f"Warning: Config file not found: {path}")
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    print(f"Warning: Empty YAML file: {path}")
                    return {}
                return data
        except Exception as e:
            print(f"Warning: Failed to load config file {path}: {e}")
            return {}
    
    def save_yaml(self, data: Dict[str, Any], file_path: Union[str, Path]):
        """保存YAML文件"""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.config_dir / path
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def _normalize_model_name(self, file_stem: str) -> str:
        """将文件名转换回原始模型名"""
        mappings = {
            'RV-Qwen2.5-S2-latest':'RV-Qwen2.5-S2:latest',
            'qwen2.5-coder-14b': 'qwen2.5-coder:14b',
            'qwen2.5-coder-32b': 'qwen2.5-coder:32b',
            'qwen2.5-14b': 'qwen2.5:14b',
            'qwen2.5-7b': 'qwen2.5:7b',
            'qwen2.5-7b-instruct-fp16': 'qwen2.5:7b-instruct-fp16',
            'qwen3-30b-a3b-fp16': 'qwen3:30b-a3b-fp16',
            'qwq-latest': 'qwq:latest',
            'qwq-32b': 'qwq:32b',
            'qwq-32b-q8_0': 'qwq:32b-q8_0',
            'deepseek-coder-33b': 'deepseek-coder:33b',
            'deepseek-coder-6.7b': 'deepseek-coder:6.7b',
            'deepseek-r1-70b': 'deepseek-r1:70b',
            'deepseek-r1-32b': 'deepseek-r1:32b',
            'deepseek-r1-14b': 'deepseek-r1:14b',
            'deepseek-ai-DeepSeek-V3': 'deepseek-ai/DeepSeek-V3',
            'phi4-latest': 'phi4:latest',
        }
        return mappings.get(file_stem, file_stem)
    
    def _parse_model_config(self, name: str, data: Dict[str, Any]) -> ModelConfig:
        """解析模型配置"""
        try:
            api_config = APIConfig(
                api_keys=data.get("api_keys", []),
                base_url=data.get("base_url", ""),
                timeout=data.get("timeout", 30),
                max_retries=data.get("max_retries", 3)
            )
            
            return ModelConfig(
                name=name,
                api_config=api_config,
                embedding_model=data.get("embedding_model"),
                max_tokens=data.get("max_tokens"),
                temperature=data.get("temperature", 0.7)
            )
        except Exception as e:
            print(f"Error parsing model config for {name}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def load_models_config(self) -> Dict[str, ModelConfig]:
        """加载所有模型配置"""
        models = {}
        models_dir = self.config_dir / "models"
        
        # print(f"Loading models from directory: {models_dir}")
        # print(f"Directory exists: {models_dir.exists()}")
        
        if models_dir.exists():
            yaml_files = list(models_dir.glob("*.yaml"))
            # print(f"Found {len(yaml_files)} YAML files")
            
            if yaml_files:
                for model_file in yaml_files:
                    try:
                        # print(f"Processing file: {model_file}")
                        
                        # 直接读取文件而不是通过 load_yaml 方法
                        with open(model_file, 'r', encoding='utf-8') as f:
                            model_data = yaml.safe_load(f)
                        
                        # print(f"  Raw data: {model_data}")
                        
                        if model_data and isinstance(model_data, dict):
                            # 使用映射方法还原模型名称
                            model_name = self._normalize_model_name(model_file.stem)
                            model_config = self._parse_model_config(model_name, model_data)
                            models[model_name] = model_config
                            # print(f"  ✅ Loaded: {model_file.stem} -> {model_name}")
                        else:
                            print(f"  ⚠️ Invalid or empty data in {model_file.name}")
                            
                    except Exception as e:
                        print(f"  ❌ Error loading {model_file.name}: {e}")
                        import traceback
                        traceback.print_exc()
                
                # print(f"Successfully loaded {len(models)} models total")
                return models
        
        print("No model config files found or directory doesn't exist, using default models")
        return self._get_default_models()
    
    def _get_default_models(self) -> Dict[str, ModelConfig]:
        """获取默认模型配置"""
        default_configs = {
            "qwen2.5-coder:14b": {
                "api_keys": ["ollama"],
                "base_url": "http://10.130.149.18:11434/v1"
            },
            "deepseek-chat": {
                "api_keys": ["sk-example"],
                "base_url": "https://api.deepseek.com"
            }
        }
        
        models = {}
        for model_name, config in default_configs.items():
            api_config = APIConfig(
                api_keys=config["api_keys"],
                base_url=config["base_url"]
            )
            models[model_name] = ModelConfig(name=model_name, api_config=api_config)
        
        print(f"Using built-in default models: {list(models.keys())}")
        return models
    
    def load_base_config(self) -> Dict[str, Any]:
        """加载基础配置"""
        base_config = self.load_yaml("base.yaml")
        
        if not base_config:
            print("No base config found, creating default...")
            base_config = self._create_default_base_config()
            self.save_yaml(base_config, "base.yaml")
        
        return base_config
    
    def _create_default_base_config(self) -> Dict[str, Any]:
        """创建默认基础配置"""
        # 尝试从已有模型中选择默认模型
        default_model = "qwen2.5-coder:14b"
        
        return {
            "debug": False,
            "environment": "development",
            "current_model": default_model,
            "agents": {
                "CoderAgent": {
                    "max_retry_attempts": 2,
                    "max_auto_fix_attempts": 2,
                    "template_dir": "agents/prompts"
                },
                "Reviewer": {
                    "max_retry_attempts": 2,
                    "max_auto_fix_attempts": 2,
                    "template_dir": "agents/prompts"
                },
                "Executor": {
                    "timeout": 2
                },
                "Summarizer": {
                    "output_format": "json"
                }
            },
            "rag": {
                "enabled": False,
                "knowledge_base_path": "./knowledge_base/RAG-data",
                "detail_knowledge_base_path": "./knowledge_base/RAG-data-detail",
                "index_path": "./knowledge_base/RAG-data/vector_index.faiss",
                "data_path": "./knowledge_base/RAG-data/vector_data.json",
                "embedding_model": "nomic-embed-text:latest",
                "llm_model": "qwen2.5-coder:14b",
                "ollama_host": "http://localhost:11434",
                "ollama_timeout": 30
            },
            "experiments": {
                "root_dir": "./TC/Datasets-TC",
                "output_base_dir": "./experiments_output-v0-merged",
                "target_experiments": []
            },
            "logging": {
                "level": "INFO",
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "file_enabled": True,
                "console_enabled": True
            },
            "agent_system_messages": {}
        }
    
    def load_environment_config(self, env: str) -> Dict[str, Any]:
        """加载环境特定配置"""
        return self.load_yaml(f"environments/{env}.yaml")
    
    def load_experiment_config(self, name: str = "default") -> Dict[str, Any]:
        """加载实验配置"""
        return self.load_yaml(f"experiments/{name}.yaml")