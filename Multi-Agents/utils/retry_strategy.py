# utils/retry_strategy.py - 智能重试策略系统
"""智能重试策略系统"""

import time
import random
import logging
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from src.core.exceptions import AgentError, ErrorCategory

class RetryErrorType(Enum):
    """重试错误类型"""
    COMPILATION_ERROR = "compilation_error"
    SIMULATION_ERROR = "simulation_error"
    LLM_API_ERROR = "llm_api_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_ERROR = "resource_error"

class BackoffStrategy(Enum):
    """退避策略"""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    RANDOM = "random"

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: bool = True
    escalation_factor: float = 2.0

@dataclass
class RetryAttempt:
    """重试尝试记录"""
    attempt_number: int
    error_type: RetryErrorType
    error_message: str
    timestamp: float
    delay_before: float = 0.0
    success: bool = False

class RetryStrategy:
    """智能重试策略"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 默认策略配置
        self.strategies: Dict[RetryErrorType, RetryConfig] = {
            RetryErrorType.COMPILATION_ERROR: RetryConfig(
                max_retries=3,
                backoff_strategy=BackoffStrategy.LINEAR,
                base_delay=2.0,
                max_delay=10.0
            ),
            RetryErrorType.SIMULATION_ERROR: RetryConfig(
                max_retries=2,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                base_delay=1.0,
                max_delay=15.0
            ),
            RetryErrorType.LLM_API_ERROR: RetryConfig(
                max_retries=5,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                base_delay=1.0,
                max_delay=60.0,
                escalation_factor=2.0
            ),
            RetryErrorType.TIMEOUT_ERROR: RetryConfig(
                max_retries=2,
                backoff_strategy=BackoffStrategy.LINEAR,
                base_delay=5.0,
                max_delay=30.0
            ),
            RetryErrorType.VALIDATION_ERROR: RetryConfig(
                max_retries=1,
                backoff_strategy=BackoffStrategy.NONE
            ),
            RetryErrorType.NETWORK_ERROR: RetryConfig(
                max_retries=4,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                base_delay=2.0,
                max_delay=30.0
            ),
            RetryErrorType.RESOURCE_ERROR: RetryConfig(
                max_retries=3,
                backoff_strategy=BackoffStrategy.FIBONACCI,
                base_delay=5.0,
                max_delay=60.0
            )
        }
        
        # 全局重试统计
        self.global_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "total_delay_time": 0.0
        }
    
    def should_retry(self, error_type: RetryErrorType, attempt_count: int, 
                    retry_history: List[RetryAttempt] = None) -> bool:
        """判断是否应该重试"""
        config = self.strategies.get(error_type, RetryConfig())
        
        # 基本重试次数检查
        if attempt_count >= config.max_retries:
            return False
        
        # 检查重试历史模式
        if retry_history and len(retry_history) >= 3:
            # 如果最近3次都是同样的错误，降低重试概率
            recent_errors = [attempt.error_type for attempt in retry_history[-3:]]
            if all(err == error_type for err in recent_errors):
                if error_type in [RetryErrorType.VALIDATION_ERROR, RetryErrorType.COMPILATION_ERROR]:
                    return False  # 这些错误重复出现时通常不会自愈
        
        return True
    
    def get_delay(self, error_type: RetryErrorType, attempt_count: int) -> float:
        """计算延迟时间"""
        config = self.strategies.get(error_type, RetryConfig())
        
        if config.backoff_strategy == BackoffStrategy.NONE:
            delay = 0.0
        elif config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = config.base_delay * (attempt_count + 1)
        elif config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.escalation_factor ** attempt_count)
        elif config.backoff_strategy == BackoffStrategy.FIBONACCI:
            delay = config.base_delay * self._fibonacci(attempt_count + 1)
        elif config.backoff_strategy == BackoffStrategy.RANDOM:
            delay = random.uniform(config.base_delay, config.base_delay * 3)
        else:
            delay = config.base_delay
        
        # 限制最大延迟
        delay = min(delay, config.max_delay)
        
        # 添加抖动
        if config.jitter and delay > 0:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0.0, delay)
    
    def _fibonacci(self, n: int) -> int:
        """计算斐波那契数"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def execute_with_retry(
        self, 
        operation: Callable,
        error_type: RetryErrorType,
        operation_name: str = "operation",
        context: Dict[str, Any] = None
    ) -> Any:
        """执行操作并重试"""
        retry_history: List[RetryAttempt] = []
        attempt_count = 0
        
        while True:
            try:
                result = operation()
                
                # 记录成功
                if retry_history:
                    self.global_stats["successful_retries"] += 1
                    self.logger.info(f"Operation {operation_name} succeeded after {attempt_count} retries")
                
                return result
                
            except Exception as e:
                attempt_count += 1
                self.global_stats["total_attempts"] += 1
                
                # 创建重试记录
                attempt = RetryAttempt(
                    attempt_number=attempt_count,
                    error_type=error_type,
                    error_message=str(e),
                    timestamp=time.time()
                )
                
                # 判断是否应该重试
                if not self.should_retry(error_type, attempt_count, retry_history):
                    self.global_stats["failed_retries"] += 1
                    self.logger.error(f"Operation {operation_name} failed after {attempt_count} attempts")
                    raise AgentError(
                        f"Operation failed after {attempt_count} attempts: {str(e)}",
                        context={
                            "operation": operation_name,
                            "error_type": error_type.value,
                            "retry_history": [a.__dict__ for a in retry_history],
                            **(context or {})
                        }
                    )
                
                # 计算延迟
                delay = self.get_delay(error_type, attempt_count - 1)
                attempt.delay_before = delay
                retry_history.append(attempt)
                
                # 记录重试信息
                self.logger.warning(
                    f"Operation {operation_name} failed (attempt {attempt_count}), "
                    f"retrying in {delay:.2f}s: {str(e)}"
                )
                
                # 等待
                if delay > 0:
                    self.global_stats["total_delay_time"] += delay
                    time.sleep(delay)
    
    def update_strategy(self, error_type: RetryErrorType, config: RetryConfig):
        """更新重试策略"""
        self.strategies[error_type] = config
        self.logger.info(f"Updated retry strategy for {error_type.value}")
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """获取策略统计信息"""
        return {
            "global_stats": self.global_stats,
            "strategies": {
                error_type.value: {
                    "max_retries": config.max_retries,
                    "backoff_strategy": config.backoff_strategy.value,
                    "base_delay": config.base_delay,
                    "max_delay": config.max_delay
                }
                for error_type, config in self.strategies.items()
            }
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.global_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "total_delay_time": 0.0
        }

# 重试装饰器
def retry_on_error(
    error_type: RetryErrorType,
    operation_name: str = None,
    strategy: RetryStrategy = None
):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal operation_name, strategy
            
            if operation_name is None:
                operation_name = func.__name__
            
            if strategy is None:
                strategy = RetryStrategy()
            
            def operation():
                return func(*args, **kwargs)
            
            return strategy.execute_with_retry(
                operation,
                error_type,
                operation_name,
                context={"function": func.__name__, "args_count": len(args)}
            )
        return wrapper
    return decorator

# 全局重试策略实例
_global_retry_strategy = RetryStrategy()

def get_retry_strategy() -> RetryStrategy:
    """获取全局重试策略实例"""
    return _global_retry_strategy