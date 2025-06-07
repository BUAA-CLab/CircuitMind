
# src/core/messaging.py
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from abc import ABC, abstractmethod
import logging
import time

class MessageType(Enum):
    """消息类型枚举"""
    VERILOG_CODE = "verilog_code"
    COMPILATION_ERROR = "compilation_error"
    EXECUTION_SUCCESS = "execution_success"
    CODE_FEEDBACK = "code_feedback"
    DESIGN_REQUEST = "design_request"
    SIMULATION_ERROR = "simulation_error"
    TEST_FAILURE = "test_failure"
    STOP_COMMAND = "stop_command"
    AGENT_STOPPED = "agent_stopped"

@dataclass
class Message:
    """标准消息格式"""
    type: MessageType
    sender: str
    receiver: str
    content: Any
    metadata: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

class MessageHandler(ABC):
    """消息处理器接口"""
    
    @abstractmethod
    async def handle(self, message: Message) -> None:
        """处理消息"""
        pass

class MessageMiddleware(ABC):
    """消息中间件接口"""
    
    @abstractmethod
    async def process(self, message: Message) -> Message:
        """处理消息，返回处理后的消息"""
        pass

class LoggingMiddleware(MessageMiddleware):
    """日志中间件"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    async def process(self, message: Message) -> Message:
        self.logger.debug(
            f"Message: {message.sender} -> {message.receiver} "
            f"({message.type.value}): {str(message.content)[:100]}..."
        )
        return message

class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self._handlers: Dict[str, List[MessageHandler]] = {}
        self._middlewares: List[MessageMiddleware] = []
        self._logger = logging.getLogger(__name__)
    
    def add_middleware(self, middleware: MessageMiddleware):
        """添加中间件"""
        self._middlewares.append(middleware)
    
    def subscribe(self, receiver: str, handler: MessageHandler):
        """订阅消息"""
        if receiver not in self._handlers:
            self._handlers[receiver] = []
        self._handlers[receiver].append(handler)
    
    def unsubscribe(self, receiver: str, handler: MessageHandler):
        """取消订阅"""
        if receiver in self._handlers:
            self._handlers[receiver].remove(handler)
    
    async def publish(self, message: Message):
        """发布消息"""
        try:
            # 应用中间件
            processed_message = message
            for middleware in self._middlewares:
                processed_message = await middleware.process(processed_message)
            
            # 发送给指定接收者
            handlers = self._handlers.get(processed_message.receiver, [])
            if not handlers:
                self._logger.warning(f"No handlers for receiver: {processed_message.receiver}")
                return
            
            # 并发处理所有处理器
            tasks = [handler.handle(processed_message) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self._logger.error(f"Error publishing message: {e}")
    
    def publish_sync(self, message: Message):
        """同步发布消息（兼容现有代码）"""
        try:
            # 简化的同步版本，不使用中间件
            handlers = self._handlers.get(message.receiver, [])
            if not handlers:
                self._logger.warning(f"No handlers for receiver: {message.receiver}")
                return
            
            # 同步处理
            for handler in handlers:
                if hasattr(handler, 'handle_sync'):
                    handler.handle_sync(message)
                else:
                    # 如果处理器只有异步方法，在新的事件循环中运行
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(handler.handle(message))
                        loop.close()
                    except Exception as e:
                        self._logger.error(f"Error in async handler: {e}")
        except Exception as e:
            self._logger.error(f"Error in sync publish: {e}")

