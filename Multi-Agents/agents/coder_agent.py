# agents/coder_agent_optimized.py - 优化版CoderAgent示例
"""优化的CoderAgent实现"""

import re
import json
from typing import Any, Dict, List, Optional
from transitions import State
from agent_base import StateMachineAgent
from mediator import Mediator
from utils.utils import extract_code_blocks, clean_code_block
from utils.retry_strategy import get_retry_strategy, RetryErrorType, retry_on_error
from utils.metrics import get_metrics_collector
from src.core.exceptions import AgentError, ValidationError, LLMAPIError, handle_errors
from src.config import get_config_manager

class CoderAgent(StateMachineAgent):
    """优化的代码生成智能体"""

    # 状态定义
    states = [
        State(name='idle'),
        State(name='generating_code'),
        State(name='handling_error'),
        State(name='reviewing_feedback'),
        State(name='waiting_for_execution_result'),
        State(name='running_simulation'),
        State(name='failure'),
        State(name='stopped')
    ]

    # 状态转换定义
    transitions = [
        {'trigger': 'design_received', 'source': 'idle', 'dest': 'generating_code'},
        {'trigger': 'code_generated', 'source': 'generating_code', 'dest': 'running_simulation'},
        {'trigger': 'execution_success', 'source': 'running_simulation', 'dest': 'idle'},
        {'trigger': 'handle_error', 'source': ['running_simulation', 'generating_code'], 'dest': 'reviewing_feedback'},
        {'trigger': 'review_feedback', 'source': 'generating_code', 'dest': 'reviewing_feedback', 
         'conditions': 'not_max_retries', 'before': 'increment_retry_count'},
        {'trigger': 'process_feedback', 'source': 'reviewing_feedback', 'dest': 'generating_code', 
         'before': 'update_prompt_based_on_feedback'},
        {'trigger': 'max_retries_reached', 'source': '*', 'dest': 'failure'},
        {'trigger': 'stop', 'source': '*', 'dest': 'stopped'}
    ]

    def __init__(self, name: str, mediator: Mediator, config, rag_tool, dff_file_path: str = './agents/dff.v'):
        super().__init__(
            name=name, 
            mediator=mediator, 
            config=config, 
            states=self.states,
            transitions=self.transitions,
            initial_state='idle',
            role="coder"
        )
        
        # 获取优化后的组件
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config("CoderAgent")
        self.metrics = get_metrics_collector()
        self.retry_strategy = get_retry_strategy()
        
        # 设置状态机钩子
        self.machine.on_enter_generating_code('generate_code_action')
        self.machine.on_enter_handling_error('handle_error_action')
        self.machine.on_enter_reviewing_feedback('handle_review_feedback_action')
        self.machine.on_enter_failure('on_enter_failure')
        self.machine.on_enter_stopped('on_enter_stopped')
        self.machine.on_enter_running_simulation('run_simulation_action')
        
        # 注册消息处理器
        self.register_message_handlers()
        
        # 初始化组件
        self.RAG = rag_tool
        self.RAG_Enable = config.rag.enabled if rag_tool else False
        self.retry_count = 0
        self.max_internal_iterations = self.agent_config.max_retry_attempts
        
        # 加载DFF模块代码
        self.dff_module_code = self._load_dff_module(dff_file_path)
        
        # 代码生成统计
        self.generation_stats = {
            "total_attempts": 0,
            "successful_generations": 0,
            "dff_analyses_performed": 0,
            "rag_queries": 0
        }
    
    @handle_errors(default_return="")
    def _load_dff_module(self, dff_file_path: str) -> str:
        """加载DFF模块代码"""
        try:
            with open(dff_file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            self._log("warning", f"DFF module file not found: {dff_file_path}")
            return ""
    
    def register_message_handlers(self):
        """注册消息处理器"""
        handlers = {
            self.MSG_TYPE_DESIGN_REQUEST: self._handle_design_request,
            self.MSG_TYPE_COMPILATION_ERROR: self._handle_error_message,
            self.MSG_TYPE_SIMULATION_ERROR: self._handle_error_message,
            self.MSG_TYPE_TEST_FAILURE: self._handle_test_failure,
            self.MSG_TYPE_ERROR: self._handle_error_message,
            self.MSG_TYPE_CODE_FEEDBACK: self._handle_code_feedback,
            self.MSG_TYPE_EXECUTION_SUCCESS: self._handle_execution_success,
            self.MSG_TYPE_SIMULATION_TIMEOUT: self._handle_simulation_timeout,
            self.MSG_TYPE_STOP_COMMAND: self._handle_stop_command
        }
        
        for msg_type, handler in handlers.items():
            self.register_message_handler(msg_type, handler)
    
    # 状态机条件和动作
    def not_max_retries(self):
        """检查是否未达到最大重试次数"""
        return self.retry_count < self.agent_config.max_retry_attempts

    def increment_retry_count(self):
        """增加重试计数"""
        self.retry_count += 1
        self._log("info", f"Retry count incremented to {self.retry_count}")

    # 状态机动作方法
    @handle_errors()
    def generate_code_action(self):
        """生成代码动作"""
        self._log("info", "Entering code generation state")
        self.generation_stats["total_attempts"] += 1
        
        # 记录指标
        experiment_name = self._get_current_experiment_name()
        self.metrics.record_code_generation(experiment_name, self.name, attempt_number=self.retry_count + 1)
        
        # 获取设计需求
        design_requirements = self.mediator.get_agent_states(self.name).get("session_design_requirements", "")
        if not design_requirements:
            raise ValidationError("No design requirements found")
        
        # 分析DFF需求
        if not self.session.analyzed_dff_need:
            analysis = self.analyze_design_requirements(design_requirements)
            self.required_components = self.retrieve_data(design_requirements)
            self.session.dff_analysis_result = analysis
            self.session.analyzed_dff_need = True
            self.generation_stats["dff_analyses_performed"] += 1
        else:
            analysis = self.session.dff_analysis_result

        # 处理分析结果
        if isinstance(analysis, list):
            self._log("warning", f"Analysis returned as list: {analysis}")
            analysis = analysis[0] if analysis else {"needs_flip_flop": False}

        # RAG检索
        retrieved_results = None
        if self.RAG_Enable and self.RAG:
            retrieved_results = self.retrieve_rag_information(self.required_components)
            self.generation_stats["rag_queries"] += 1

        # 构建提示并生成代码
        dff_code = self.dff_module_code if analysis.get("needs_flip_flop") else None
        
        prompt_content = self.build_prompt(
            design_requirements=design_requirements,
            error_message=getattr(self.session, 'last_error_message', ""),
            reviewer_feedback=getattr(self.session, 'reviewer_feedback', ""),
            dff_code=dff_code,
            retrieved_results=retrieved_results
        )
        
        # 使用重试策略生成代码
        try:
            response_text = self.retry_strategy.execute_with_retry(
                lambda: self.session.get_response(custom_prompt=prompt_content),
                RetryErrorType.LLM_API_ERROR,
                "code_generation",
                context={"agent": self.name, "retry_count": self.retry_count}
            )
            
            verilog_code = clean_code_block(self.parse_response(response_text))
            
            if not verilog_code.startswith("// Error"):
                self.session.last_generated_code = verilog_code
                self.generation_stats["successful_generations"] += 1
                self.send_code_to_reviewer(verilog_code, design_requirements)
            else:
                raise AgentError("Failed to generate valid Verilog code")
                
        except Exception as e:
            self._log("error", "Code generation failed", error_type="generation_error")
            if not self.shutdown_requested:
                self.handle_error(error_message=str(e))

    @handle_errors()
    def handle_error_action(self, error_message=None):
        """处理错误动作"""
        self._log("info", f"Handling error: {error_message or 'Unknown error'}")
        
        # 记录错误指标
        experiment_name = self._get_current_experiment_name()
        self.metrics.record_error(experiment_name, "agent_error", error_message, self.name)
        
        if self.retry_count >= self.agent_config.max_retry_attempts:
            self._log("warning", "Max retries reached, triggering final simulation")
            self._attempt_final_simulation()
            self.max_retries_reached(error_message=error_message)
        else:
            self.session.add_message("user", f"Error: {error_message}. Please try again.")
            self.review_feedback()

    def _attempt_final_simulation(self):
        """尝试最终仿真"""
        last_message = next(
            (msg for msg in reversed(self.session.messages) if msg['role'] == 'assistant'), 
            None
        )
        
        if last_message:
            verilog_code = clean_code_block(self.parse_response(last_message['content']))
            if not verilog_code.startswith("// Error"):
                self._log("info", "Sending final code to Executor")
                self.send_message(["Executor"], {
                    "type": self.MSG_TYPE_VERILOG_CODE,
                    "content": verilog_code
                })

    @handle_errors()
    def handle_review_feedback_action(self, **kwargs):
        """处理审查反馈动作"""
        self._log("info", "Processing review feedback")
        
        error_message = kwargs.get("error_message")
        if error_message:
            self._log("info", f"Received error: {error_message}")

        feedback_content = getattr(self.session, 'last_feedback_content', {})
        needs_revision = feedback_content.get("needs_revision", False)
        
        if self.retry_count >= self.agent_config.max_retry_attempts:
            self._log("warning", "Max retries reached during feedback processing")
            self.max_retries_reached(error_message=feedback_content.get("feedback"))
        else:
            if needs_revision:
                feedback_message = feedback_content.get("feedback", "")
                suggestion = feedback_content.get("suggestion", "")
                line_number = feedback_content.get("line", -1)
                
                error_msg = (f"Line {line_number}: {feedback_message}. Suggestion: {suggestion}" 
                           if line_number != -1 
                           else f"{feedback_message}. Suggestion: {suggestion}")
                
                self.session.add_message("user", f"Error: {error_msg}")
                self.session.last_feedback_message = error_msg
            
            self.stop()

    @handle_errors()
    def run_simulation_action(self):
        """运行仿真动作"""
        if not self.session.last_generated_code:
            raise AgentError("No generated code available for simulation")
            
        self._log("info", "Sending code to Executor for simulation")
        self.send_message(["Executor"], {
            "type": self.MSG_TYPE_VERILOG_CODE,
            "content": self.session.last_generated_code
        })
        self.safe_trigger('waiting_for_execution_result')

    def on_enter_failure(self, error_message=None):
        """进入失败状态"""
        self._log("info", f"Entering failure state: {error_message}")
        self.send_message(["UserProxy"], {
            "type": "code_generation_failed",
            "content": f"Code generation failed: {error_message}"
        })

    def on_enter_stopped(self):
        """进入停止状态"""
        self._log("info", "Agent stopped")
        self.send_message(["UserProxy"], {"type": "agent_stopped"})

    # 业务逻辑方法
    @retry_on_error(RetryErrorType.LLM_API_ERROR, "dff_analysis")
    @handle_errors(default_return={"needs_flip_flop": False, "reason": "Analysis failed"})
    def analyze_design_requirements(self, design_requirements: str) -> Dict[str, Any]:
        """分析设计需求以确定是否需要D触发器"""
        prompt = f"""
Analyze the following Verilog design requirements and determine if a d flip-flop or register is needed.

Design Requirements:
{design_requirements}

Respond in JSON format:
{{"needs_flip_flop": true/false, "reason": "explanation"}}
"""
        try:
            model_config = self.config_manager.get_model_config()
            
            response = self.client.chat.completions.create(
                model=model_config.name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are an expert hardware design assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            self._log("debug", f"DFF analysis result: {result}")
            return result
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            raise LLMAPIError(f"Error analyzing design requirements: {e}")

    @handle_errors(default_return=[])
    def retrieve_data(self, design_requirements: str) -> List[str]:
        """检索所需组件数据"""
        prompt = f"""
Analyze the following digital circuit design requirements and determine which fundamental logic gates or components are needed.

Design Requirements:
{design_requirements}

Respond in JSON format:
{{
"required_components": ["xor", "not", "and", "or", "mux", ...],
"reason": "Explanation"
}}
"""
        try:
            model_config = self.config_manager.get_model_config()
            
            response = self.client.chat.completions.create(
                model=model_config.name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are an expert hardware design assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result.get("required_components", [])
            
        except Exception as e:
            self._log("error", f"Error retrieving component data: {e}")
            return []

    @handle_errors(default_return="")
    def retrieve_rag_information(self, components: List[str]) -> str:
        """从RAG系统检索信息"""
        if not self.RAG or not components:
            return ""
            
        retrieved_results = ""
        for query in components:
            if query.lower() not in ['and', 'not', 'or']:
                try:
                    retrieved = self.RAG.retrieve_coder(query)
                    retrieved_results += f"{retrieved}\n"
                except Exception as e:
                    self._log("warning", f"RAG retrieval failed for {query}: {e}")
        
        self._log("debug", f"RAG retrieval results: {len(retrieved_results)} chars")
        return retrieved_results

    def build_prompt(self, design_requirements: str, error_message: str = "", 
                    reviewer_feedback: str = "", dff_code: str = None, 
                    retrieved_results: str = "") -> str:
        """构建LLM提示"""
        template_name = getattr(self.session, 'template_name', "generate_code_generic.j2")
        
        template_context = {
            "design_requirements": design_requirements,
            "error_message": error_message,
            "reviewer_feedback": reviewer_feedback,
            "retry_count": self.retry_count,
            "dff_module_code": dff_code,
            "retrieved_results": {"content": retrieved_results} if retrieved_results else None,
            "retrieved_information": {"errors": []}
        }
        
        return self._render_template(template_name, **template_context)

    @handle_errors(default_return="// Error: No code found")
    def parse_response(self, response_text: str) -> str:
        """解析LLM响应中的Verilog代码"""
        code_blocks = extract_code_blocks(response_text)
        if code_blocks:
            code = code_blocks[-1].strip()
            self._log("debug", f"Extracted Verilog code: {len(code)} chars")
            return code
        
        self._log("error", "No Verilog code blocks found in response")
        return "// Error: No Verilog code blocks found."

    def send_code_to_reviewer(self, verilog_code: str, design_requirements: str):
        """发送代码到审查者"""
        dff_analysis = getattr(self.session, 'dff_analysis_result', {"needs_flip_flop": False})
        
        self._log("info", f"Sending code to Reviewer (attempt {self.retry_count + 1})")
        self.send_message(["Reviewer"], {
            "type": self.MSG_TYPE_VERILOG_CODE,
            "content": verilog_code,
            "attempt_count": self.retry_count,
            "dff_analysis": dff_analysis,
            "design_requirements": design_requirements
        })

    # 消息处理器
    @handle_errors()
    def _handle_design_request(self, message, sender=None):
        """处理设计请求"""
        design_req = message.get("content", "")
        if not design_req:
            raise ValidationError("Empty design request received")
        
        self.mediator.update_agent_state(self.name, {"session_design_requirements": design_req})
        self._log("info", f"Received design requirements: {design_req[:100]}...")
        
        self.session.add_message("user", design_req)
        self.safe_trigger('design_received')

    @handle_errors()
    def _handle_error_message(self, message, sender=None):
        """处理错误消息"""
        error_message = message.get("content", "")
        self._log("info", f"Received error from {sender}: {error_message}")
        
        if self.state in ['generating_code', 'running_simulation']:
            if self.retry_count >= self.agent_config.max_retry_attempts:
                self.safe_trigger('max_retries_reached', error_message=error_message)
            else:
                self.safe_trigger('review_feedback')

    @handle_errors()
    def _handle_code_feedback(self, message, sender=None):
        """处理代码反馈"""
        feedback_content = message.get("content", {})
        self._log("info", f"Received feedback from {sender}")
        
        self.session.last_feedback_content = feedback_content
        
        # 存储代码和执行结果
        if feedback_content.get("code"):
            self.session.last_feedback_code = feedback_content["code"]
        
        if feedback_content.get("execution_result"):
            self.session.last_feedback_execution_result = feedback_content["execution_result"]
        
        self.safe_trigger('stop')

    @handle_errors()
    def _handle_execution_success(self, message, sender=None):
        """处理执行成功消息"""
        content = message.get("content", "")
        self._log("info", "Received execution success message")
        
        if "Failed" in content:
            self.safe_trigger('handle_error', error_message="Test execution failed")
        else:
            self.safe_trigger('stop')

    @handle_errors()
    def _handle_simulation_timeout(self, message, sender=None):
        """处理仿真超时"""
        error_message = message.get("content", "")
        self._log("warning", f"Simulation timeout: {error_message}")
        self.safe_trigger('handle_error', error_message=f"Simulation timeout: {error_message}")

    @handle_errors()
    def _handle_test_failure(self, message, sender=None):
        """处理测试失败"""
        error_message = message.get("content", "")
        self._log("info", f"Test failure: {error_message}")
        
        if self.state in ['generating_code', 'running_simulation']:
            if self.retry_count >= self.agent_config.max_retry_attempts:
                self.safe_trigger('max_retries_reached', error_message=error_message)
            else:
                self.safe_trigger('handle_error', error_message=error_message)

    def _handle_stop_command(self, message, sender=None):
        """处理停止命令"""
        self._log("info", "Received stop command")
        self.safe_trigger('stop')

    # 辅助方法
    def _get_current_experiment_name(self) -> str:
        """获取当前实验名称"""
        # 这应该从某个地方获取当前实验的名称
        # 可以从mediator或配置中获取
        return getattr(self, 'current_experiment', 'unknown_experiment')

    def update_prompt_based_on_feedback(self):
        """基于反馈更新提示"""
        self._log("info", "Updating prompt based on feedback")
        feedback_content = getattr(self.session, 'last_feedback_content', {})
        self.session.template_name = "generate_code_generic.j2"
        self.session.reviewer_feedback = getattr(self.session, 'last_feedback_message', "")

    def get_generation_stats(self) -> Dict[str, Any]:
        """获取代码生成统计信息"""
        stats = self.generation_stats.copy()
        stats.update({
            "current_retry_count": self.retry_count,
            "max_retries": self.agent_config.max_retry_attempts,
            "success_rate": (stats["successful_generations"] / max(1, stats["total_attempts"])) * 100
        })
        return stats