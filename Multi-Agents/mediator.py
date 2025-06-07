# mediator.py
from typing import Any, Dict, List
from utils.logger import setup_logger
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from src.config import get_config_manager
import os

class Mediator:
    def __init__(self):
        self.agents: Dict[str, 'Agent'] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}  # 用于存储代理的状态
        self.logger = setup_logger("Mediator")
        self.latest_code: Dict[str, Dict[str, str]] = {} # 用于存储每个会话中每个代理的最新代码
        self.latest_simulation_results: Dict[str, Dict[str, Any]] = {} # 用于存储每个会话的最新仿真结果
        
        # Get configuration manager
        self.config_manager = get_config_manager()

    def register_agent(self, agent_name: str, agent: 'Agent'):
        self.agents[agent_name] = agent
        self.agent_states[agent_name] = {}  
        self.latest_code[agent_name] = {} 
        self.logger.debug(f"Agent '{agent_name}' has been registered with the mediator.")

    def send_message(self, sender: str, receivers: List[str], message: Any):
        for receiver in receivers:
            self.logger.debug(f"Mediator received a message from '{sender}' to agent '{receiver}'.")
            if receiver in self.agents:
                self.agents[receiver].receive_message(sender, message)
            else:
                self.logger.error(f"Target agent '{receiver}' is not registered.")

    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """
        Returns the state information of the specified agent.
        """
        if agent_name in self.agent_states:
            return self.agent_states[agent_name]
        else:
            self.logger.error(f"Unable to get state for agent '{agent_name}': agent not registered or state not initialized.")
            return {}

    def update_agent_state(self, agent_name: str, state: Dict[str, Any]):
        """
        Updates the state information of the specified agent.
        """
        if agent_name in self.agent_states:
            self.agent_states[agent_name].update(state)
            # self.logger.debug(f"State of agent '{agent_name}' updated: {state}")
        else:
            self.logger.error(f"Unable to update state for agent '{agent_name}': agent not registered.")

    def get_agent_design_requirements(self, agent_name: str, session_id: str) -> str:
        """
        Returns the design requirements for a specific session of an agent.
        """
        if agent_name in self.agent_states and "session_design_requirements" in self.agent_states[agent_name] and session_id in self.agent_states[agent_name]["session_design_requirements"]:
            return self.agent_states[agent_name]["session_design_requirements"][session_id]
        else:
            self.logger.error(f"Unable to get design requirements for agent '{agent_name}', session '{session_id}'.")
            return ""

    def get_dff_module_code(self, agent_name: str) -> str:
        """
        Returns the dff_module_code of a specific agent.
        """
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            if hasattr(agent, 'dff_module_code'):
                return agent.dff_module_code
            else:
                self.logger.error(f"Agent '{agent_name}' does not have 'dff_module_code' attribute.")
                return None
        else:
            self.logger.error(f"Agent '{agent_name}' not found.")
            return None

    def store_latest_code(self, sender: str, session_id: str, code: str):
        """Stores the latest Verilog code for a given agent and session."""
        if sender not in self.latest_code:
            self.latest_code[sender] = {}
        self.latest_code[sender][session_id] = code
        self.logger.debug(f"Stored latest code from {sender} for session {session_id}.")

    def get_latest_code(self, sender: str, session_id: str) -> str:
        """Retrieves the latest Verilog code for a given agent and session."""
        if sender in self.latest_code and session_id in self.latest_code[sender]:
            return self.latest_code[sender][session_id]
        else:
            self.logger.warning(f"No latest code found for {sender} in session {session_id}.")
            return ""

    def store_latest_simulation_result(self, session_id: str, result: Dict[str, Any]):
        """Stores the latest simulation result for a given session."""
        self.latest_simulation_results[session_id] = result
        self.logger.debug(f"Stored latest simulation result for session {session_id}: {result}")

    def get_latest_simulation_result(self, session_id: str) -> Dict[str, Any]:
        """Retrieves the latest simulation result for a given session."""
        return self.latest_simulation_results.get(session_id, {})

    def get_agent_states(self, agent_name: str) -> Dict[str, Any]:
        """
        Returns all state information for the specified agent.
        """
        if agent_name in self.agent_states:
            return self.agent_states[agent_name]
        else:
            self.logger.error(f"Unable to get states for agent '{agent_name}': agent not registered.")
            return {}

class Agent:
    def __init__(self, name: str, mediator: Mediator, config: Dict[str, Any]):
        self.name = name
        self.mediator = mediator
        self.logger = setup_logger(self.name)
        self.config = config  # Store the app config
        self.mediator.register_agent(self.name, self)
        
        # Get configuration manager and model config
        try:
            self.config_manager = get_config_manager()
            self.model_config = self.config_manager.get_model_config()
            
            # Initialize OpenAI client with current model configuration
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=self.model_config.base_url
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration for agent {name}: {e}")
            # Fallback: try to use old-style config access if available
            if hasattr(config, 'OPENAI_API_KEY') and hasattr(config, 'OPENAI_BASE_URL'):
                self.logger.warning(f"Using fallback configuration for agent {name}")
                self.client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL
                )
            else:
                self.logger.error(f"No valid configuration found for agent {name}")
                raise
        
        # Initialize Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), './agents/prompts')
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,    # 移除块后的第一个换行
            lstrip_blocks=True   # 移除块前的空白
        )

    def send_message(self, receivers: List[str], message: Any):
        self.logger.debug(f"Agent '{self.name}' is sending a message to {receivers}.")
        self.mediator.send_message(self.name, receivers, message)

    def receive_message(self, sender: str, message: Any):
        raise NotImplementedError("Subclasses must implement the 'receive_message' method.")

    def update_model_config(self):
        """Update model configuration when model is switched."""
        try:
            self.model_config = self.config_manager.get_model_config()
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=self.model_config.base_url
            )
        except Exception as e:
            self.logger.error(f"Failed to update model configuration: {e}")