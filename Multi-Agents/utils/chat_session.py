# utils/chat_session.py - 兼容版ChatSession
"""兼容的聊天会话管理类"""

import re
import json
import logging
from typing import Any, Dict, Optional, List
from openai import OpenAI, APIStatusError
from colorama import Fore, Style
from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from utils.llm_client_pool import get_llm_client_pool
from src.config import get_config_manager
import time

class ChatSession:
    """兼容的聊天会话管理类"""
    
    def __init__(self, config, system_message=None, role=None):
        self.messages = []
        self.system_message = system_message
        self.role = role
        self.app_config = config
        
        self.logger = setup_logger(f"ChatSession-{role}" if role else "ChatSession")
        
        # 获取配置管理器和客户端池
        self.config_manager = get_config_manager()
        self.client_pool = get_llm_client_pool()
        
        # 设置默认系统消息
        if system_message is None:
            system_messages = config.agent_system_messages
            self.system_message = system_messages.get(
                "DefaultAgent", 
                "You are a helpful assistant."
            )
        
        # 初始化会话状态
        self.reset_session_state()
    
    def reset_session_state(self):
        """重置会话状态"""
        self.last_generated_code = None
        self.analyzed_dff_need = False
        self.dff_analysis_result = {"needs_flip_flop": False}
        self.template_name = "generate_code_generic.j2"
        self.last_feedback_content = {}
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        if not content or not content.strip():
            self.logger.warning("Attempting to add empty message")
            return
        
        self.messages.append({"role": role, "content": content.strip()})
        self.logger.debug(f"Added {role} message ({len(content)} chars)")
    
    def _format_content(self, content) -> str:
        """格式化内容用于日志显示"""
        if isinstance(content, (list, dict)):
            try:
                if self.logger.level <= logging.DEBUG:
                    return json.dumps(content, indent=2, ensure_ascii=False)
                else:
                    return str(content)
            except:
                return str(content)
        elif isinstance(content, str):
            if len(content) > 500 and self.logger.level > logging.DEBUG:
                return content[:500] + "..."
            return re.sub(r'\\s{2,}', ' ', content).strip()
        else:
            return str(content)
    
    def get_response(self, custom_prompt: str = None, response_format: Dict = None) -> str:
        """获取LLM响应"""
        try:
            # 获取当前模型配置
            model_config = self.config_manager.get_model_config()
            
            # 从客户端池获取客户端
            client = self.client_pool.get_client(model_config)
            
            # 准备消息
            messages_for_llm = self.messages.copy()
            if custom_prompt:
                messages_for_llm.append({"role": "user", "content": custom_prompt})
            
            # 添加系统消息
            if self.system_message and not any(msg["role"] == "system" for msg in messages_for_llm):
                messages_for_llm.insert(0, {"role": "system", "content": self.system_message})
            
            # 记录提示
            self._log_llm_prompt(messages_for_llm)
            
            # 准备API参数
            api_params = {
                "model": model_config.name,
                "messages": messages_for_llm
            }
            
            # 添加可选参数
            if hasattr(model_config, 'temperature') and model_config.temperature is not None:
                api_params["temperature"] = model_config.temperature
            
            if hasattr(model_config, 'max_tokens') and model_config.max_tokens is not None:
                api_params["max_tokens"] = model_config.max_tokens
            
            if response_format:
                api_params["response_format"] = response_format
            
            # 调用LLM (简化版，无复杂重试)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(**api_params)
                    response_content = response.choices[0].message.content.strip()
                    
                    # 记录响应
                    self._log_llm_response(response_content)
                    
                    # 添加到对话历史
                    self.add_message("assistant", response_content)
                    
                    return response_content
                    
                except APIStatusError as e:
                    self.logger.warning(f"API error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 简单退避
                        continue
                    else:
                        return f"// Error: LLM API Error: {e.status_code}"
                
                except Exception as e:
                    self.logger.error(f"Unexpected error in LLM call: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return f"// Error: Failed to get LLM response: {str(e)}"
            
            return "// Error: Max retries reached"
            
        except Exception as e:
            self.logger.error(f"Failed to get LLM response: {str(e)}")
            return f"// Error: {str(e)}"
    
    def _log_llm_prompt(self, messages: List[Dict]):
        """记录LLM提示"""
        formatted_prompt = f"""
{Fore.BLUE}===================== LLM Call - Prompt ====================={Style.RESET_ALL}
{self._format_content(messages)}
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
    
    def reset_session(self):
        """重置聊天会话"""
        self.messages.clear()
        self.reset_session_state()
        self.logger.info("Chat session reset")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        return {
            "message_count": len(self.messages),
            "has_generated_code": bool(self.last_generated_code),
            "analyzed_dff": self.analyzed_dff_need
        }
    
    def update_model_config(self):
        """更新模型配置"""
        # 清除客户端池缓存，确保使用新配置
        self.client_pool.clear_all()
        self.logger.info("ChatSession model configuration updated")