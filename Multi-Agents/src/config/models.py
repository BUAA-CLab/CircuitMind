# src/config/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os

@dataclass
class APIConfig:
    """API配置"""
    api_keys: List[str]
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    current_key_index: int = 0
    
    def get_current_key(self) -> str:
        """获取当前API密钥"""
        if not self.api_keys:
            raise ValueError("No API keys configured")
        return self.api_keys[self.current_key_index]
    
    def switch_key(self) -> str:
        """切换到下一个API密钥"""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.get_current_key()

@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    api_config: APIConfig
    embedding_model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    
    @property
    def api_key(self) -> str:
        return self.api_config.get_current_key()
    
    @property
    def base_url(self) -> str:
        return self.api_config.base_url

@dataclass
class AgentConfig:
    """智能体配置"""
    max_retry_attempts: int = 2
    max_auto_fix_attempts: int = 2
    template_dir: str = "agents/prompts"
    system_message: Optional[str] = None
    timeout: Optional[int] = None  # 添加 timeout 字段
    
@dataclass
class RAGConfig:
    """RAG配置"""
    enabled: bool = False
    knowledge_base_path: str = "./knowledge_base/RAG-data"
    detail_knowledge_base_path: str = "./knowledge_base/RAG-data-detail"
    index_path: str = "./knowledge_base/RAG-data/vector_index.faiss"
    data_path: str = "./knowledge_base/RAG-data/vector_data.json"
    embedding_model: str = "nomic-embed-text:latest"
    llm_model: str = "qwen2.5-coder:14b"
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: int = 30

@dataclass
class ExperimentConfig:
    """实验配置"""
    root_dir: str = "./TC/Datasets-TC"
    output_base_dir: str = "./experiments_output"
    target_experiments: List[str] = field(default_factory=list)
    verilog_dir: Optional[str] = None
    testbench_path: Optional[str] = None
    reference_code_path: Optional[str] = None
    summary_file: Optional[str] = None
    
    def get_output_dir(self, model_name: str) -> str:
        """获取模型特定的输出目录"""
        return str(Path(self.output_base_dir) / f"v0-merged/{model_name}")

@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_enabled: bool = True
    console_enabled: bool = True

@dataclass
class AppConfig:
    """应用主配置"""
    # 基础配置
    debug: bool = False
    environment: str = "development"
    
    # 当前选中的模型
    current_model: str = "qwen2.5-coder:14b"
    
    # 各模块配置
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    rag: RAGConfig = field(default_factory=RAGConfig)
    experiments: ExperimentConfig = field(default_factory=ExperimentConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # 系统消息配置
    agent_system_messages: Dict[str, str] = field(default_factory=dict)
    
    def get_current_model_config(self) -> ModelConfig:
        """获取当前模型配置"""
        if self.current_model not in self.models:
            raise ValueError(f"Model {self.current_model} not configured")
        return self.models[self.current_model]
    
    def switch_model(self, model_name: str):
        """切换模型"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        self.current_model = model_name
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """获取智能体配置"""
        return self.agents.get(agent_name, AgentConfig())