# agent_base.py - 兼容版BaseAgent
"""兼容的智能体基类"""

from typing import Any, Dict, List, Optional, Callable
from transitions import State
from transitions.extensions.markup import MarkupMachine as Machine
from mediator import Mediator, Agent
from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from utils.chat_session import ChatSession
from colorama import Fore, Style, init
from src.config import get_config_manager
import time

init(autoreset=True)

class BaseAgent(Agent):
    """兼容的智能体基类"""
    
    # 标准化消息类型
    MSG_TYPE_VERILOG_CODE = "verilog_code"
    MSG_TYPE_ERROR = "error"
    MSG_TYPE_CODE_FEEDBACK = "code_feedback"
    MSG_TYPE_EXECUTION_SUCCESS = "execution_success"
    MSG_TYPE_SIMULATION_TIMEOUT = "simulation_timeout"
    MSG_TYPE_TEST_FAILURE = "test_failure"
    MSG_TYPE_STOP_COMMAND = "stop_command"
    MSG_TYPE_DESIGN_REQUEST = "design_request"
    MSG_TYPE_COMPILATION_ERROR = "compilation_error"
    MSG_TYPE_SIMULATION_ERROR = "simulation_error"
    
    def __init__(self, name: str, mediator: Mediator, config: Dict[str, Any], role: str = "agent"):
        """初始化基础智能体"""
        super().__init__(name, mediator, config)
        self.logger = setup_logger(name)
        self.app_config = config
        self.role = role
        
        # 获取配置管理器和智能体配置
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config(name)
        
        # 获取系统消息
        system_messages = config.agent_system_messages
        self.system_message = system_messages.get(
            name, 
            f"You are a helpful {name} assistant."
        )
        
        # 初始化聊天会话
        self.session = ChatSession(
            config=config, 
            system_message=self.system_message, 
            role=role
        )
        
        # 消息处理器映射
        self._message_handlers = {}
        
        self.logger.info(f"Initialized {name} agent with role: {role}")
    
    def _log(self, level: str, message: str, **kwargs):
        """简化的日志记录"""
        getattr(self.logger, level)(message)
    
    def _log_dialogue(self, message: str):
        """记录对话级别日志"""
        self.logger.log(DIALOGUE_LOG_LEVEL, f"===DIALOGUE-Note===\\n{message}")
    
    def _log_llm_prompt(self, prompt: str):
        """记录LLM提示"""
        formatted_prompt = f"""
{Fore.BLUE}===================== LLM Call - Prompt ====================={Style.RESET_ALL}
{prompt}
{Fore.BLUE}==========================================================={Style.RESET_ALL}
"""
        self.logger.log(DIALOGUE_LOG_LEVEL, formatted_prompt)
    
    def _log_llm_response(self, response: str):
        """记录LLM响应"""
        formatted_response = f"""
{Fore.GREEN}==================== LLM Call - Response ===================={Style.RESET_ALL}
{response}
{Fore.GREEN}==========================================================={Style.RESET_ALL}
"""
        self.logger.log(DIALOGUE_LOG_LEVEL, formatted_response)
    
    def send_message(self, receivers: List[str], message: Dict[str, Any]):
        """发送消息到指定接收者"""
        if not receivers:
            self.logger.warning("No receivers specified for message")
            return
        
        if not isinstance(message, dict) or "type" not in message:
            self.logger.warning("Invalid message format")
            return
        
        self._log("debug", f"Sending message to {receivers}")
        self.mediator.send_message(self.name, receivers, message)
    
    def register_message_handler(self, msg_type: str, handler_method: Callable):
        """注册消息处理器"""
        if not msg_type or not callable(handler_method):
            self.logger.warning("Invalid message handler registration")
            return
        
        self._message_handlers[msg_type] = handler_method
        self._log("debug", f"Registered handler for message type: {msg_type}")
    
    def receive_message(self, sender: str, message: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = message.get("type", "")
        self._log("debug", f"Received message from {sender}: {msg_type}")
        
        if msg_type in self._message_handlers:
            handler = self._message_handlers[msg_type]
            self._log("debug", f"Delegating to handler: {handler.__name__}")
            
            try:
                handler(message, sender)
            except Exception as e:
                self.logger.error(f"Error in message handler {handler.__name__}: {str(e)}")
        else:
            self._log("warning", f"No handler for message type: {msg_type}")
    
    def _render_template(self, template_name: str, **kwargs) -> str:
        """渲染模板"""
        try:
            template = self.template_env.get_template(template_name)
            rendered = template.render(**kwargs)
            self._log_dialogue(f"Rendered template {template_name}")
            return rendered
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            return f"Template rendering failed: {e}"
    
    def get_llm_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """获取LLM响应"""
        if not prompt or not prompt.strip():
            self.logger.warning("Empty prompt provided to LLM")
            return "// Error: Empty prompt"
        
        system_msg = system_message if system_message else self.system_message
        self._log_llm_prompt(prompt)
        
        # 临时覆盖系统消息
        if system_message:
            original_system_message = self.session.system_message
            self.session.system_message = system_message
        
        try:
            self.session.add_message("user", prompt)
            response = self.session.get_response()
            self._log_llm_response(response)
            return response
        finally:
            # 恢复原始系统消息
            if system_message:
                self.session.system_message = original_system_message
    
    def update_configuration(self):
        """更新智能体配置"""
        self.agent_config = self.config_manager.get_agent_config(self.name)
        self.session.update_model_config()
        self._log("info", f"Configuration updated for agent {self.name}")


class StateMachineAgent(BaseAgent):
    """兼容的状态机智能体基类"""
    
    def __init__(self, name: str, mediator: Mediator, config: Dict[str, Any], 
                 states: List[State], transitions: List[Dict[str, Any]], 
                 initial_state: str = 'idle', role: str = "agent"):
        """初始化状态机智能体"""
        super().__init__(name, mediator, config, role)
        
        try:
            self.machine = Machine(
                model=self, 
                states=states, 
                transitions=transitions,
                initial=initial_state,
                name=f"{name}SM"
            )
            
            self._log("info", f"Initialized state machine with states: {[s.name for s in states]}")
            self._log("info", f"Current state: {self.state}")
            
        except Exception as e:
            self._log("error", f"Failed to initialize state machine: {e}")
            raise
    
    def get_state_info(self) -> Dict[str, Any]:
        """获取状态机信息"""
        available_triggers = []
        try:
            available_triggers = [trigger for trigger in self.machine.get_triggers(self.state)]
        except:
            pass
        
        return {
            "current_state": self.state,
            "available_triggers": available_triggers,
            "state_machine_name": self.machine.name
        }
    
    def log_state_transition(self, event_data):
        """记录状态转换"""
        if hasattr(event_data, 'transition'):
            transition = event_data.transition
            self._log("debug", f"State transition: {transition.source} -> {transition.dest}")
    
    def safe_trigger(self, trigger_name: str, **kwargs) -> bool:
        """安全的状态转换触发"""
        try:
            if hasattr(self, trigger_name):
                trigger_method = getattr(self, trigger_name)
                trigger_method(**kwargs)
                self._log("debug", f"Successfully triggered: {trigger_name}")
                return True
            else:
                self._log("warning", f"Trigger {trigger_name} not available in current state {self.state}")
                return False
        except Exception as e:
            self._log("error", f"Error triggering {trigger_name}: {e}")
            return False