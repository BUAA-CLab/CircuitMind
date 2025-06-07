# agents/user_proxy.py

from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from typing import Any, Dict
from mediator import Mediator, Agent
from colorama import Fore, Style, init

init(autoreset=True)

class UserProxy(Agent):
    """
    User agent, receives user requirements and submits them to the system.
    """
    def __init__(self, name: str, mediator: Mediator, config: Dict[str, Any]):
        super().__init__(name, mediator,config)
        self.logger = setup_logger("UserProxy")
        self._log("debug", "UserProxy initialized.")

    def _log(self, level: str, message: str):
        getattr(self.logger, level)(message)

    def submit_design_request(self, design_requirements: str):
        self.logger.log(DIALOGUE_LOG_LEVEL, f"{Fore.GREEN}User submitted design request: {design_requirements}{Style.RESET_ALL}")
        self.send_message(["CoderAgent"], {
            "type": "design_request",
            "content": design_requirements
        })

    def receive_message(self, sender: str, message: Any):
        msg_type = message.get("type", "")
        if msg_type == "review_feedback":
            feedback = message.get("content")
            self._log("info", f"{Fore.YELLOW}Received design feedback: {feedback}{Style.RESET_ALL}")
        elif msg_type == "execution_result":
            result = message.get("content")
            if "执行成功" in result:
                self._log("info", f"{Fore.CYAN}Design execution result: {result}{Style.RESET_ALL}")
            else:
                self._log("warning", f"{Fore.RED}Design execution result: {result}{Style.RESET_ALL}")
        elif msg_type == "final_failure":
            failure_message = message.get("content")
            self._log("error", f"{Fore.RED}Design execution failed: {failure_message}{Style.RESET_ALL}")
        elif msg_type == "agent_stopped":
            self._log("info", f"{Fore.BLUE}Coder agent stopped{Style.RESET_ALL}")
            return 
        elif msg_type == "execution_success": 
            self._log("info", f"{Fore.CYAN}Received execution_success message (from {sender}){Style.RESET_ALL}") 
            return
        else:
            self._log("warning", f"{Fore.BLUE}Unknown message type: {msg_type}{Style.RESET_ALL}")