# utils/metrics.py - 实时监控和指标系统
"""实时监控和指标收集系统"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import logging

class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class EventType(Enum):
    """事件类型"""
    EXPERIMENT_START = "experiment_start"
    EXPERIMENT_END = "experiment_end"
    AGENT_ACTION = "agent_action"
    LLM_CALL = "llm_call"
    ERROR_OCCURRED = "error_occurred"
    STATE_TRANSITION = "state_transition"
    CODE_GENERATION = "code_generation"
    COMPILATION = "compilation"
    SIMULATION = "simulation"

@dataclass
class ExperimentMetrics:
    """实验指标"""
    experiment_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    success: bool = False
    error_count: int = 0
    llm_calls: int = 0
    compilation_attempts: int = 0
    simulation_attempts: int = 0
    code_generation_attempts: int = 0
    total_tokens: int = 0
    agent_states: Dict[str, str] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """实验持续时间"""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def success_rate(self) -> float:
        """成功率 (基于重试次数)"""
        total_attempts = max(1, self.code_generation_attempts)
        return 1.0 if self.success else 0.0

@dataclass
class AgentMetrics:
    """智能体指标"""
    agent_name: str
    role: str
    messages_sent: int = 0
    messages_received: int = 0
    errors_handled: int = 0
    llm_calls: int = 0
    state_transitions: int = 0
    current_state: str = "unknown"
    uptime: float = 0.0
    last_activity: float = field(default_factory=time.time)

@dataclass
class SystemMetrics:
    """系统整体指标"""
    total_experiments: int = 0
    successful_experiments: int = 0
    failed_experiments: int = 0
    total_llm_calls: int = 0
    total_tokens: int = 0
    total_errors: int = 0
    average_experiment_duration: float = 0.0
    start_time: float = field(default_factory=time.time)
    
    @property
    def success_rate(self) -> float:
        """系统成功率"""
        if self.total_experiments == 0:
            return 0.0
        return self.successful_experiments / self.total_experiments
    
    @property
    def uptime(self) -> float:
        """系统运行时间"""
        return time.time() - self.start_time

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # 实验指标
        self.experiments: Dict[str, ExperimentMetrics] = {}
        self.experiment_history: deque = deque(maxlen=max_history_size)
        
        # 智能体指标
        self.agents: Dict[str, AgentMetrics] = {}
        
        # 系统指标
        self.system_metrics = SystemMetrics()
        
        # 实时事件流
        self.event_stream: deque = deque(maxlen=max_history_size)
        
        # 自定义指标
        self.custom_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # 指标订阅者
        self.subscribers: List[Callable] = []
        
        self.logger.info("MetricsCollector initialized")
    
    def start_experiment(self, experiment_name: str) -> ExperimentMetrics:
        """开始实验"""
        with self.lock:
            metric = ExperimentMetrics(experiment_name=experiment_name)
            self.experiments[experiment_name] = metric
            self.system_metrics.total_experiments += 1
            
            self._emit_event(EventType.EXPERIMENT_START, {
                "experiment_name": experiment_name,
                "timestamp": metric.start_time
            })
            
            self.logger.info(f"Started experiment: {experiment_name}")
            return metric
    
    def finish_experiment(self, experiment_name: str, success: bool, 
                         final_code: str = None, error_message: str = None):
        """结束实验"""
        with self.lock:
            if experiment_name not in self.experiments:
                self.logger.warning(f"Experiment {experiment_name} not found")
                return
            
            metric = self.experiments[experiment_name]
            metric.end_time = time.time()
            metric.success = success
            
            # 更新系统指标
            if success:
                self.system_metrics.successful_experiments += 1
            else:
                self.system_metrics.failed_experiments += 1
            
            # 计算平均实验时间
            total_duration = sum(exp.duration for exp in self.experiments.values() if exp.end_time)
            finished_count = len([exp for exp in self.experiments.values() if exp.end_time])
            if finished_count > 0:
                self.system_metrics.average_experiment_duration = total_duration / finished_count
            
            # 移动到历史记录
            self.experiment_history.append(metric)
            
            self._emit_event(EventType.EXPERIMENT_END, {
                "experiment_name": experiment_name,
                "success": success,
                "duration": metric.duration,
                "error_message": error_message
            })
            
            self.logger.info(f"Finished experiment: {experiment_name} (success: {success})")
    
    def record_agent_activity(self, agent_name: str, activity_type: str, 
                            role: str = None, current_state: str = None):
        """记录智能体活动"""
        with self.lock:
            if agent_name not in self.agents:
                self.agents[agent_name] = AgentMetrics(
                    agent_name=agent_name,
                    role=role or "unknown"
                )
            
            agent_metric = self.agents[agent_name]
            agent_metric.last_activity = time.time()
            
            if current_state:
                if agent_metric.current_state != current_state:
                    agent_metric.state_transitions += 1
                agent_metric.current_state = current_state
            
            # 根据活动类型更新计数
            if activity_type == "message_sent":
                agent_metric.messages_sent += 1
            elif activity_type == "message_received":
                agent_metric.messages_received += 1
            elif activity_type == "error_handled":
                agent_metric.errors_handled += 1
            elif activity_type == "llm_call":
                agent_metric.llm_calls += 1
                self.system_metrics.total_llm_calls += 1
            
            self._emit_event(EventType.AGENT_ACTION, {
                "agent_name": agent_name,
                "activity_type": activity_type,
                "current_state": current_state
            })
    
    def record_llm_call(self, experiment_name: str, agent_name: str = None, 
                       tokens_used: int = 0, model_name: str = None):
        """记录LLM调用"""
        with self.lock:
            # 记录实验级别的LLM调用
            if experiment_name in self.experiments:
                self.experiments[experiment_name].llm_calls += 1
                if tokens_used > 0:
                    self.experiments[experiment_name].total_tokens += tokens_used
                    self.system_metrics.total_tokens += tokens_used
            
            # 记录智能体级别的LLM调用
            if agent_name:
                self.record_agent_activity(agent_name, "llm_call")
            
            self._emit_event(EventType.LLM_CALL, {
                "experiment_name": experiment_name,
                "agent_name": agent_name,
                "tokens_used": tokens_used,
                "model_name": model_name
            })
    
    def record_error(self, experiment_name: str, error_type: str, 
                    error_message: str = None, agent_name: str = None):
        """记录错误"""
        with self.lock:
            # 记录实验级别错误
            if experiment_name in self.experiments:
                self.experiments[experiment_name].error_count += 1
                if error_type not in self.experiments[experiment_name].error_types:
                    self.experiments[experiment_name].error_types[error_type] = 0
                self.experiments[experiment_name].error_types[error_type] += 1
            
            # 记录智能体级别错误
            if agent_name:
                self.record_agent_activity(agent_name, "error_handled")
            
            # 更新系统错误计数
            self.system_metrics.total_errors += 1
            
            self._emit_event(EventType.ERROR_OCCURRED, {
                "experiment_name": experiment_name,
                "error_type": error_type,
                "error_message": error_message,
                "agent_name": agent_name
            })
    
    def record_code_generation(self, experiment_name: str, agent_name: str = None, 
                              success: bool = True, attempt_number: int = 1):
        """记录代码生成"""
        with self.lock:
            if experiment_name in self.experiments:
                self.experiments[experiment_name].code_generation_attempts += 1
            
            self._emit_event(EventType.CODE_GENERATION, {
                "experiment_name": experiment_name,
                "agent_name": agent_name,
                "success": success,
                "attempt_number": attempt_number
            })
    
    def record_compilation(self, experiment_name: str, success: bool = True, 
                          error_message: str = None):
        """记录编译"""
        with self.lock:
            if experiment_name in self.experiments:
                self.experiments[experiment_name].compilation_attempts += 1
            
            self._emit_event(EventType.COMPILATION, {
                "experiment_name": experiment_name,
                "success": success,
                "error_message": error_message
            })
    
    def record_simulation(self, experiment_name: str, success: bool = True, 
                         duration: float = 0.0, timeout: bool = False):
        """记录仿真"""
        with self.lock:
            if experiment_name in self.experiments:
                self.experiments[experiment_name].simulation_attempts += 1
            
            self._emit_event(EventType.SIMULATION, {
                "experiment_name": experiment_name,
                "success": success,
                "duration": duration,
                "timeout": timeout
            })
    
    def record_state_transition(self, agent_name: str, from_state: str, 
                               to_state: str, trigger: str = None):
        """记录状态转换"""
        with self.lock:
            self.record_agent_activity(agent_name, "state_transition", current_state=to_state)
            
            self._emit_event(EventType.STATE_TRANSITION, {
                "agent_name": agent_name,
                "from_state": from_state,
                "to_state": to_state,
                "trigger": trigger
            })
    
    def set_custom_metric(self, category: str, name: str, value: Any):
        """设置自定义指标"""
        with self.lock:
            self.custom_metrics[category][name] = {
                "value": value,
                "timestamp": time.time()
            }
    
    def increment_custom_counter(self, category: str, name: str, increment: int = 1):
        """增加自定义计数器"""
        with self.lock:
            if category not in self.custom_metrics:
                self.custom_metrics[category] = {}
            
            if name not in self.custom_metrics[category]:
                self.custom_metrics[category][name] = {"value": 0, "timestamp": time.time()}
            
            self.custom_metrics[category][name]["value"] += increment
            self.custom_metrics[category][name]["timestamp"] = time.time()
    
    def _emit_event(self, event_type: EventType, data: Dict[str, Any]):
        """发出事件"""
        event = {
            "type": event_type.value,
            "timestamp": time.time(),
            "data": data
        }
        
        self.event_stream.append(event)
        
        # 通知订阅者
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """订阅事件"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_experiment_summary(self, experiment_name: str = None) -> Dict[str, Any]:
        """获取实验摘要"""
        with self.lock:
            if experiment_name:
                if experiment_name in self.experiments:
                    return asdict(self.experiments[experiment_name])
                else:
                    return {}
            
            # 返回所有实验的摘要
            current_experiments = {name: asdict(metric) for name, metric in self.experiments.items()}
            historical_experiments = [asdict(metric) for metric in self.experiment_history]
            
            return {
                "current_experiments": current_experiments,
                "historical_experiments": historical_experiments
            }
    
    def get_agent_summary(self, agent_name: str = None) -> Dict[str, Any]:
        """获取智能体摘要"""
        with self.lock:
            if agent_name:
                if agent_name in self.agents:
                    metric = self.agents[agent_name]
                    summary = asdict(metric)
                    summary["uptime"] = time.time() - summary["last_activity"]
                    return summary
                else:
                    return {}
            
            # 返回所有智能体摘要
            return {
                name: {**asdict(metric), "uptime": time.time() - metric.last_activity}
                for name, metric in self.agents.items()
            }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """获取系统摘要"""
        with self.lock:
            summary = asdict(self.system_metrics)
            summary["custom_metrics"] = dict(self.custom_metrics)
            summary["active_experiments"] = len(self.experiments)
            summary["active_agents"] = len(self.agents)
            
            # 计算最近事件统计
            recent_events = [event for event in self.event_stream 
                           if time.time() - event["timestamp"] < 3600]  # 最近1小时
            
            event_counts = defaultdict(int)
            for event in recent_events:
                event_counts[event["type"]] += 1
            
            summary["recent_events"] = dict(event_counts)
            summary["total_events"] = len(self.event_stream)
            
            return summary
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """获取实时统计"""
        with self.lock:
            # 最近5分钟的活动
            cutoff_time = time.time() - 300
            recent_events = [event for event in self.event_stream 
                           if event["timestamp"] > cutoff_time]
            
            # 活跃的智能体
            active_agents = [
                name for name, metric in self.agents.items()
                if time.time() - metric.last_activity < 60  # 最近1分钟活跃
            ]
            
            # 进行中的实验
            running_experiments = [
                name for name, metric in self.experiments.items()
                if metric.end_time is None
            ]
            
            return {
                "recent_activity_count": len(recent_events),
                "active_agents": active_agents,
                "running_experiments": running_experiments,
                "system_load": {
                    "total_experiments": self.system_metrics.total_experiments,
                    "success_rate": self.system_metrics.success_rate,
                    "avg_duration": self.system_metrics.average_experiment_duration,
                    "total_llm_calls": self.system_metrics.total_llm_calls,
                    "total_errors": self.system_metrics.total_errors
                }
            }
    
    def export_metrics(self, format: str = "json") -> str:
        """导出指标数据"""
        with self.lock:
            data = {
                "system_metrics": self.get_system_summary(),
                "experiments": self.get_experiment_summary(),
                "agents": self.get_agent_summary(),
                "events": list(self.event_stream)
            }
            
            if format.lower() == "json":
                return json.dumps(data, indent=2, default=str)
            else:
                return str(data)
    
    def reset_metrics(self):
        """重置所有指标"""
        with self.lock:
            self.experiments.clear()
            self.experiment_history.clear()
            self.agents.clear()
            self.system_metrics = SystemMetrics()
            self.event_stream.clear()
            self.custom_metrics.clear()
            
            self.logger.info("All metrics reset")

# 全局指标收集器
_global_metrics = MetricsCollector()

def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    return _global_metrics

# 装饰器用于自动记录指标
def track_experiment(experiment_name: str = None):
    """实验跟踪装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal experiment_name
            if experiment_name is None:
                experiment_name = func.__name__
            
            metrics = get_metrics_collector()
            metrics.start_experiment(experiment_name)
            
            try:
                result = func(*args, **kwargs)
                metrics.finish_experiment(experiment_name, success=True)
                return result
            except Exception as e:
                metrics.record_error(experiment_name, type(e).__name__, str(e))
                metrics.finish_experiment(experiment_name, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator

def track_llm_call(experiment_name: str = None, agent_name: str = None):
    """LLM调用跟踪装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            
            try:
                result = func(*args, **kwargs)
                # 尝试从结果中提取token信息
                tokens = 0
                if hasattr(result, 'usage') and result.usage:
                    tokens = result.usage.total_tokens
                
                metrics.record_llm_call(
                    experiment_name or "unknown",
                    agent_name,
                    tokens
                )
                return result
            except Exception as e:
                metrics.record_error(
                    experiment_name or "unknown",
                    "llm_error",
                    str(e),
                    agent_name
                )
                raise
        return wrapper
    return decorator