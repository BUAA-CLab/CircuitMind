# src/core/exceptions.py - 增强版异常系统
"""优化的异常处理系统"""

import json
import time
from typing import Dict, Any, Optional
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    CONFIGURATION = "configuration"
    NETWORK = "network"
    LLM_API = "llm_api"
    COMPILATION = "compilation"
    SIMULATION = "simulation"
    VALIDATION = "validation"
    SYSTEM = "system"

class CircuitMindError(Exception):
    """基础异常类 - 增强版"""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式便于日志记录"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "context": self.context,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        return f"[{self.category.value.upper()}] {self.message}"

class ConfigurationError(CircuitMindError):
    """配置错误"""
    def __init__(self, message: str, config_file: str = None, **kwargs):
        context = kwargs.get('context', {})
        if config_file:
            context['config_file'] = config_file
        
        super().__init__(
            message, 
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            context=context,
            recoverable=False,
            **kwargs
        )

class LLMAPIError(CircuitMindError):
    """LLM API 相关错误"""
    def __init__(self, message: str, status_code: int = None, model_name: str = None, **kwargs):
        context = kwargs.get('context', {})
        if status_code:
            context['status_code'] = status_code
        if model_name:
            context['model_name'] = model_name
        
        # 根据状态码判断是否可恢复
        recoverable = status_code in [429, 500, 502, 503, 504] if status_code else True
        severity = ErrorSeverity.HIGH if status_code in [401, 403] else ErrorSeverity.MEDIUM
        
        super().__init__(
            message,
            category=ErrorCategory.LLM_API,
            severity=severity,
            context=context,
            recoverable=recoverable,
            **kwargs
        )

class AgentError(CircuitMindError):
    """智能体错误"""
    def __init__(self, message: str, agent_name: str = None, state: str = None, **kwargs):
        context = kwargs.get('context', {})
        if agent_name:
            context['agent_name'] = agent_name
        if state:
            context['current_state'] = state
        
        super().__init__(
            message,
            category=ErrorCategory.SYSTEM,
            context=context,
            **kwargs
        )

class CompilationError(CircuitMindError):
    """编译错误"""
    def __init__(self, message: str, code_file: str = None, line_number: int = None, **kwargs):
        context = kwargs.get('context', {})
        if code_file:
            context['code_file'] = code_file
        if line_number:
            context['line_number'] = line_number
        
        super().__init__(
            message,
            category=ErrorCategory.COMPILATION,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            recoverable=True,
            **kwargs
        )

class SimulationError(CircuitMindError):
    """仿真错误"""
    def __init__(self, message: str, timeout: bool = False, **kwargs):
        context = kwargs.get('context', {})
        context['timeout'] = timeout
        
        super().__init__(
            message,
            category=ErrorCategory.SIMULATION,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            recoverable=True,
            **kwargs
        )

class ValidationError(CircuitMindError):
    """验证错误"""
    def __init__(self, message: str, validation_type: str = None, **kwargs):
        context = kwargs.get('context', {})
        if validation_type:
            context['validation_type'] = validation_type
        
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            context=context,
            recoverable=True,
            **kwargs
        )

class TemplateError(CircuitMindError):
    """模板错误"""
    def __init__(self, message: str, template_name: str = None, **kwargs):
        context = kwargs.get('context', {})
        if template_name:
            context['template_name'] = template_name
        
        super().__init__(
            message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            recoverable=True,
            **kwargs
        )

class ServiceError(CircuitMindError):
    """服务错误"""
    def __init__(self, message: str, service_name: str = None, **kwargs):
        context = kwargs.get('context', {})
        if service_name:
            context['service_name'] = service_name
        
        super().__init__(
            message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            context=context,
            recoverable=False,
            **kwargs
        )

# 错误处理装饰器
def handle_errors(default_return=None, log_errors=True):
    """错误处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CircuitMindError as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.error(f"Business error in {func.__name__}: {e.to_dict()}")
                if e.recoverable:
                    return default_return
                else:
                    raise
            except Exception as e:
                if log_errors and hasattr(args[0], 'logger'):
                    args[0].logger.critical(f"Unexpected error in {func.__name__}: {str(e)}")
                if default_return is not None:
                    return default_return
                else:
                    raise AgentError(f"Unexpected error in {func.__name__}: {str(e)}")
        return wrapper
    return decorator