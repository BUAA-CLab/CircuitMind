# reviewer.py

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from transitions import State
from agent_base import StateMachineAgent
from mediator import Mediator
from utils.utils import extract_code_blocks, clean_code_block
from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from colorama import Fore, Style, init
from src.config import get_config_manager

init(autoreset=True)

class Reviewer(StateMachineAgent):
    """
    Agent responsible for reviewing Verilog code, providing feedback,
    and communicating with the Executor for code simulation.
    Uses a state machine approach for managing workflow.
    """
    
    # Define states for the state machine
    states = [
        State(name='idle'),
        State(name='initializing_review'),
        State(name='reviewing_code'),
        State(name='executing_code'),
        State(name='processing_results'),
        State(name='complete')
    ]
    
    # Define transitions between states
    transitions = [
        # Normal flow transitions
        {'trigger': 'start_review', 'source': 'idle', 'dest': 'initializing_review'},
        {'trigger': 'init_complete', 'source': 'initializing_review', 'dest': 'reviewing_code'},
        {'trigger': 'review_complete', 'source': 'reviewing_code', 'dest': 'executing_code'},
        {'trigger': 'execution_complete', 'source': 'executing_code', 'dest': 'processing_results'},
        
        # Error handling and retry transitions
        {'trigger': 'retry_review', 'source': ['processing_results', 'initializing_review', 'executing_code'], 'dest': 'reviewing_code'},
        
        # Completion transitions
        {'trigger': 'finish_review', 'source': '*', 'dest': 'complete'},
        {'trigger': 'restart_review', 'source': '*', 'dest': 'idle'}
    ]
    
    def __init__(self, name: str, mediator: Mediator, config, rag_tool, dff_file_path: str = './agents/dff.v'):
        """
        Initialize the Reviewer agent.
        
        Args:
            name: Agent name
            mediator: Mediator for agent communication
            config: Application configuration from new config system
            rag_tool: RAG system for retrieving relevant information
            dff_file_path: Path to the D flip-flop module code
        """
        super().__init__(
            name=name, 
            mediator=mediator, 
            config=config, 
            states=self.states,
            transitions=self.transitions,
            initial_state='idle',
            role="reviewer"
        )
        
        # Get configuration manager and agent config
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config("Reviewer")
        
        # Set up state machine hooks
        self.machine.on_enter_initializing_review('on_enter_initializing_review')
        self.machine.on_enter_reviewing_code('on_enter_reviewing_code')
        self.machine.on_enter_executing_code('on_enter_executing_code')
        self.machine.on_enter_processing_results('on_enter_processing_results')
        self.machine.on_enter_complete('on_enter_complete')
        
        # Register message handlers
        self.register_message_handlers()
        
        # Initialize agent-specific attributes using new config
        self.RAG = rag_tool
        self.RAG_Enable = config.rag.enabled if rag_tool else False
        self.auto_fix_attempts = 0
        self.max_auto_fix_attempts = self.agent_config.max_auto_fix_attempts
        self.current_code = ""
        self.previous_execution_result = ""
        self.structural_result = None
        self.needs_review = True
        self.error_type = None
        self.design_requirements = ""
        self.previous_state_before_execute = None
        self.dff_analysis_result = {'needs_flip_flop': False}
        self.is_auto_correction = False
        self.execution_success = False
        self.execution_code = ""
        self.is_timeout = False
        
        # Load the D flip-flop module code
        try:
            with open(dff_file_path, 'r') as f:
                self.dff_module_code = f.read()
        except FileNotFoundError:
            self._log("warning", f"DFF module file not found: {dff_file_path}")
            self.dff_module_code = ""
    
    def register_message_handlers(self):
        """Register handlers for different message types."""
        self.register_message_handler(self.MSG_TYPE_DESIGN_REQUEST, self._handle_design_request)
        self.register_message_handler(self.MSG_TYPE_VERILOG_CODE, self._handle_verilog_code)
        self.register_message_handler(self.MSG_TYPE_EXECUTION_SUCCESS, self._handle_execution_success)
        self.register_message_handler("execution_result_and_code", self._handle_execution_result)
        self.register_message_handler(self.MSG_TYPE_COMPILATION_ERROR, self._handle_executor_error)
        self.register_message_handler(self.MSG_TYPE_SIMULATION_ERROR, self._handle_executor_error)
        self.register_message_handler(self.MSG_TYPE_TEST_FAILURE, self._handle_executor_error)
        self.register_message_handler("agent_stopped", self._handle_agent_stopped)
    
    # State machine action methods
    def on_enter_initializing_review(self):
        """Action when entering initializing_review state."""
        self._log("info", "Entering initializing_review state.")
        self.current_code = self._correct_format()
        self._send_code_to_executor(self.current_code, False, self.needs_review)
        
    def on_enter_reviewing_code(self, attempt_num=None, error_type=None):
        """Action when entering reviewing_code state."""
        self._log("info", "Entering reviewing_code state.")
        attempt_num = attempt_num if attempt_num is not None else self.auto_fix_attempts
        error_type = error_type if error_type is not None else self.error_type
        
        output_json_format = attempt_num >= self.max_auto_fix_attempts
        review_result = self._review_code(
            self.current_code, 
            self.design_requirements, 
            attempt_num, 
            self.previous_execution_result, 
            error_type, 
            output_json_format
        )
        self._log("debug", f"output_json_format is {output_json_format}")

        if isinstance(review_result, dict):
            self.structural_result = review_result
            self.needs_review = review_result.get("needs_revision", False)
            self._log("info", f"Review returned json result. Needs revision = {self.needs_review}")
            
            if self.needs_review:
                if self.auto_fix_attempts < self.max_auto_fix_attempts:
                    # Stay in reviewing_code state for another attempt
                    self.auto_fix_attempts += 1
                    self.on_enter_reviewing_code(self.auto_fix_attempts, error_type)
                else:
                    self.send_feedback_to_coder(
                        self.structural_result, 
                        self.current_code, 
                        {"success": False, "execution_result": self.previous_execution_result}, 
                        needs_revision=True, 
                        feedback_reason="Max auto-fix attempts reached, sending feedback."
                    )
                    self.finish_review()
            else:
                self.previous_state_before_execute = 'reviewing_code'
                self.review_complete()
        elif isinstance(review_result, str):
            self.current_code = review_result
            self.previous_state_before_execute = 'reviewing_code'
            self._log("info", "Review returned Verilog code, proceeding to execution.")
            self.review_complete()
        else:
            self._log("error", f"Unexpected review_code result type: {type(review_result)}")
            self.finish_review()
        
    def on_enter_executing_code(self):
        """Action when entering executing_code state."""
        self._log("info", "Entering executing_code state.")
        is_auto_correction_value = self.previous_state_before_execute == 'reviewing_code'
        self._send_code_to_executor(self.current_code, is_auto_correction_value, self.needs_review)
        
    def on_enter_processing_results(self):
        """Action when entering processing_results state."""
        self._log("info", "Entering processing_results state.")
        
        success = self.execution_success
        execution_result = self.previous_execution_result
        code = self.execution_code if hasattr(self, 'execution_code') else self.current_code
        is_auto_correction = self.is_auto_correction
        
        if is_auto_correction:
            if success and "All tests passed" in execution_result:
                self._log("info", "Automatic correction successful. Tests passed.")
                cleaned_code = re.sub(r'^\s*```\s*verilog\s*|^\s*```\s*|^\s*```|```\s*$', '', code, flags=re.MULTILINE).strip()
                self.send_message(["UserProxy"], {"type": "code_generation_successful", "content": cleaned_code})
                self.finish_review()
            elif self.auto_fix_attempts >= self.max_auto_fix_attempts:
                self._log("info", "Max auto-fix attempts reached. Finishing review.")
                self.finish_review()
            else:
                self._log("warning", "Automatic correction failed after simulation.")
                if self.auto_fix_attempts < self.max_auto_fix_attempts:
                    self.auto_fix_attempts += 1
                    self.retry_review()
                else:
                    self.send_feedback_to_coder(
                        self.structural_result, 
                        code, 
                        {"success": False, "execution_result": execution_result}, 
                        needs_revision=True, 
                        feedback_reason="Automatic correction failed after simulation, max auto-fix attempts reached."
                    )
                    self.finish_review()
        else:
            self._log("info", "Initial execution result processed.")
            self._handle_normal_execution_result(success, execution_result, None)
    
    def on_enter_complete(self):
        """Action when entering complete state."""
        self._log("info", "Review process complete.")
        
    def _handle_normal_execution_result(self, success, execution_result, structural_result):
        """Handle normal (non-auto-correction) execution results."""
        if success and "All tests passed" in execution_result:
            self.send_feedback_to_coder(
                structural_result, 
                self.current_code, 
                {
                    "success": success, 
                    "execution_result": execution_result, 
                    "needs_revision": False
                }, 
                feedback_reason="All checks passed."
            )
            self._log("info", "Session passed execution.")
            cleaned_code = re.sub(r'^\s*```\s*verilog\s*|^\s*```\s*|^\s*```|```\s*$', '', self.current_code, flags=re.MULTILINE).strip()
            self.mediator.store_latest_code("Reviewer", "", cleaned_code)
            
            # Send the execution success message to Summarizer
            self.send_message(["Summarizer"], {
                "type": "execution_success",
                "content": {
                    "code": cleaned_code,
                    "execution_result": execution_result,
                    "design_requirements": self.design_requirements,
                    "structural_result": structural_result
                }
            })
            
            self.finish_review()
        else:
            self._log("info", "Tests failed, need further revision." if success else "Execution failed.")
            self.send_feedback_to_coder(
                structural_result, 
                self.current_code, 
                {
                    "success": False, 
                    "execution_result": execution_result, 
                    "needs_revision": True
                }, 
                feedback_reason="Tests failed, need further revision."
            )
            self.auto_fix_attempts += 1
            self.previous_state_before_execute = 'reviewing_code'
            self.retry_review()
            
    # Utility methods    
    def _clean_json_response(self, resp_text: str) -> Dict[str, Any]:
        """Clean and parse JSON response from LLM."""
        try:
            cleaned_text = re.sub(r'^.*?({.*}).*$', r'\1', resp_text, flags=re.DOTALL).strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            self._log("warning", f"Failed to parse JSON response: {resp_text}. Error: {e}")
            return {
                "feedback": f"Failed to parse JSON response, error: {e}", 
                "needs_revision": True, 
                "error_code": "JSONError", 
                "line": -1, 
                "suggestion": "LLM returned invalid JSON."
            }
            
    def _extract_last_verilog_code(self, resp_text: str) -> str:
        """Extract the last Verilog code block from the response text."""
        pattern = re.compile(r"```verilog\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(resp_text)
        
        if matches:
            code = matches[-1].strip()  # Extract the last matching code block
        else:
            code = ""
            self._log("warning", "No Verilog code block found in the input.")
        
        self._log("debug", f"Extracted code block: {code[:50]}...")
        return code
        
    def _send_code_to_executor(self, code: str, is_auto_correction: bool, needs_revision: bool):
        """Send code to the Executor agent for execution."""
        # Check if code is valid
        if not code or not isinstance(code, (str, bytes)):
            self._log("error", "Invalid or empty Verilog code received. Skipping execution.")
            return
            
        cleaned_code = re.sub(r'^\s*```\s*verilog\s*|^\s*```\s*|^\s*```|```\s*$', '', code, flags=re.MULTILINE).strip()
        
        # Add DFF module if needed and not already present
        if self.dff_analysis_result['needs_flip_flop'] and "module d_flip_flop" not in cleaned_code:
            cleaned_code += "\n" + self.dff_module_code
            
        self.send_message(["Executor"], {
            "type": "verilog_code",
            "content": cleaned_code,
            "is_auto_correction": is_auto_correction,
            "needs_revision": needs_revision
        })
        
    def _correct_format(self) -> str:
        """Correct the format of the Verilog code."""
        template_name = "preview.j2" 
        
        # Check if DFF is needed
        needs_flip_flop = False
        if self.dff_analysis_result is not None and isinstance(self.dff_analysis_result, dict):
            needs_flip_flop = self.dff_analysis_result.get('needs_flip_flop', False)
            
        # Extract module definition if it exists in the design requirements
        module_pattern = re.compile(r"module\s+\w+\s*\([^;]*\);", re.DOTALL)
        match = module_pattern.search(self.design_requirements)
        module_definition = match.group(0) if match else ""
        
        # Render the template
        prompt = self._render_template(
            template_name,
            design_requirements=module_definition,
            code=self.current_code if self.current_code else "",
            dff_module_code="\n" + self.dff_module_code if needs_flip_flop and "module d_flip_flop" not in (self.current_code or "") else None
        )
        
        self._log_llm_prompt(prompt)
        self.session.add_message("user", prompt)
        raw = self.session.get_response()
        self._log_llm_response(raw)
        
        extracted_verilog_code = clean_code_block(self._extract_last_verilog_code(raw))
        return extracted_verilog_code if extracted_verilog_code else self.current_code
        
    def _review_code(self, code: str, design_requirements: str, attempt_num: int = 0, 
                    previous_execution_result: str = "", error_type: str = None, 
                    output_json_format: bool = False) -> Dict[str, Any] or str:
        """
        Review code and provide feedback or corrections.
        
        Args:
            code: The Verilog code to review
            design_requirements: The design requirements
            attempt_num: The current attempt number
            previous_execution_result: The previous execution result if any
            error_type: The type of error if any
            output_json_format: Whether to return a JSON format (True) or Verilog code (False)
            
        Returns:
            Either a dictionary with feedback or a string with corrected Verilog code
        """
        # Retrieve relevant information from RAG if enabled
        if self.RAG_Enable and self.RAG:
            retrieved_results = {
                'errors_pattern': "",
                'best_practices': "",
                'circuit_designs': ""
            }
            
            if error_type in ["compilation_error", "simulation_error", "test_failure"]:
                self._log("info", f"Reviewing code for {error_type}")
                try:
                    retrieved = self.RAG.retrieve_reviewer(previous_execution_result)
                    self._log("info", "Retrieval results:")
                    
                    for i, item in enumerate(retrieved, 1):
                        self._log("info", f"\nResult {i}:")
                        if item['class'] == 'error_pattern':
                            retrieved_results["errors_pattern"] += "The problem description is:\n" + item['problem_description'] + "\nThe solution is:" + item['solution_pattern'] + "\n"
                        elif item['class'] == 'best_practices':
                            retrieved_results["best_practices"] += "The code example is:\n" + item['code_example'] + "\n"
                        elif item['class'] == 'circuit_designs':
                            retrieved_results["circuit_designs"] += "The description is:\n" + item['description'] + "The code example is:\n" + item['code_example'] + "\n"
                        self._log("info", json.dumps(item, indent=2, ensure_ascii=False))
                except Exception as e:
                    self._log("warning", f"Failed to retrieve RAG information: {e}")
        else:
            retrieved_results = None
            
        # Determine the review focus based on the error type
        review_focus = {
            "compilation_error": "compilation errors and structural Verilog syntax",
            "simulation_error": "simulation errors and functional/logical correctness",
            "test_failure": "test failures and logical correctness"
        }.get(error_type, "general structural Verilog code quality")
        
        # Prepare the template and context
        template_name = "review_code_prompt_main.j2"
        template_context = {
            "design_requirements": design_requirements if attempt_num == 0 else None,
            "code": code if attempt_num == 0 else None,
            "dff_module_code": self.dff_module_code if attempt_num == 0 and self.dff_analysis_result['needs_flip_flop'] else None,
            "output_json_format": output_json_format,
            "previous_execution_result": previous_execution_result,
            "error_type": error_type if attempt_num == 0 else None,
            "review_focus": review_focus if attempt_num == 0 else None
        }
        
        # Add retrieved results if available
        if retrieved_results:
            template_context.update({
                "retrieved_results_errors_pattern": retrieved_results.get('errors_pattern'),
                "retrieved_results_best_practices": retrieved_results.get('best_practices'),
                "retrieved_results_circuit_designs": retrieved_results.get('circuit_designs')
            })
        else:
            template_context.update({
                "retrieved_results_errors_pattern": None,
                "retrieved_results_best_practices": None,
                "retrieved_results_circuit_designs": None
            })
            
        # Render the template
        prompt = self._render_template(template_name, **template_context)
        self._log("debug", f"AUTO_CORRECT attempt {self.auto_fix_attempts+1}/{self.max_auto_fix_attempts}, Error Type: {error_type}")
        
        try:
            # Log the prompt and get the response
            self._log_llm_prompt(prompt)
            self.session.add_message("user", prompt)
            raw = self.session.get_response()
            self._log_llm_response(raw)
            
            # Process the response based on expected format
            if output_json_format:
                return self._clean_json_response(raw)
            else:
                extracted_verilog_code = clean_code_block(self._extract_last_verilog_code(raw))
                if extracted_verilog_code:
                    # Check if we unexpectedly got JSON when we wanted Verilog
                    try:
                        json.loads(raw)
                        self._log("warning", "Unexpected JSON output received when expecting Verilog code, but Verilog code also extracted.")
                        return extracted_verilog_code
                    except json.JSONDecodeError:
                        return extracted_verilog_code
                        
                self._log("warning", "No valid Verilog code extracted when expected. Returning error feedback.")
                return {
                    "feedback": "Expected Verilog output, but no valid Verilog code block found.", 
                    "needs_revision": True, 
                    "error_code": "NoVerilogCode", 
                    "line": -1, 
                    "suggestion": "LLM did not return valid Verilog code."
                }
        except Exception as e:
            self._log("error", f"Error calling LLM for code review/correction: {e}")
            return {
                "feedback": "Review error occurred, check logs.", 
                "needs_revision": True, 
                "error_code": "ReviewError", 
                "line": -1, 
                "suggestion": "Check the Reviewer's logs for errors."
            }
            
    def send_feedback_to_coder(self, structural_result: dict = None, code=None, execution_result: dict = None, 
                              needs_revision: bool = False, llm_output: str = None, feedback_reason: str = None):
        """Send feedback to the CoderAgent."""
        if self.state == 'complete':
            self._log("info", "Skipping feedback send because Reviewer is in complete state.")
            return
            
        feedback_content = ""
        needs_revision_feedback = needs_revision or (structural_result and isinstance(structural_result, dict) and structural_result.get("needs_revision"))
        
        if structural_result and isinstance(structural_result, dict) and structural_result.get("needs_revision"):
            feedback_content += f"Structural Review Failed:\n{structural_result.get('feedback')}\nSuggestion: {structural_result.get('suggestion')}\n\n"
            
        feedback_message = {
            "needs_revision": needs_revision_feedback,
            "error_code": self._determine_error_code(structural_result, None, execution_result),
            "line": structural_result.get("line") if isinstance(structural_result, dict) and structural_result.get("needs_revision") else -1,
        }
        
        if llm_output:
            feedback_message["llm_output"] = llm_output
        if code:
            feedback_message["code"] = code
        if feedback_reason:
            feedback_message["reason"] = feedback_reason
            
        self.send_message(["CoderAgent"], {
            "type": "code_feedback",
            "content": feedback_message
        })
        
        self._log_dialogue(f"Sending feedback to CoderAgent:\n{feedback_content}, Reason: {feedback_reason}")
        
    def _determine_error_code(self, structural_result, behavioral_result, execution_result):
        """Determine the error code based on the results."""
        if structural_result and isinstance(structural_result, dict) and structural_result.get("needs_revision"):
            return structural_result.get("error_code")
        elif isinstance(execution_result, dict) and not execution_result.get("success"):
            return "SimulationFailed"
        elif isinstance(execution_result, str):
            return "ExecutionError"
        return "NoSpecificIssue"
        
    def _analyze_design_for_triggers(self, design_requirements: str) -> bool:
        """Analyze design requirements for keywords that trigger special handling."""
        keywords = ["clock", "edge", "flip-flop", "register", "state machine"]
        return any(keyword in design_requirements.lower() for keyword in keywords)
    
    # Message handlers
    def _handle_design_request(self, message, sender=None):
        """Handle a design request message."""
        design_requirements = message.get("content", "")
        self._log("info", "Received design_request.")
        self.design_requirements = design_requirements
        
        # Check if the design likely requires flip-flops or registers
        needs_triggers = self._analyze_design_for_triggers(design_requirements)
        if needs_triggers:
            self._log_dialogue("Design likely requires flip-flops/registers.")
            
        self.session.add_message("user", f"The user's design requirements: {design_requirements}. A flip-flop may be needed.")
        
    def _handle_verilog_code(self, message, sender=None):
        """Process received Verilog code."""
        self._log("debug", "Processing Verilog code from sender: " + str(sender))
        code = message.get("content", "")
        
        # Store the DFF analysis if provided
        dff_analysis = message.get("dff_analysis", None)
        if self.design_requirements == "":
            self.design_requirements = message.get("design_requirements", "")
            
        if dff_analysis:
            self.dff_analysis_result.update(dff_analysis)
            self._log("debug", f"Set dff_analysis_result to: {self.dff_analysis_result}")
            self._log("info", f"Received DFF analysis from CoderAgent: {dff_analysis}")
            
        self.current_code = code
        
        # Start the review process
        if self.state == 'idle':
            self.start_review()
        
    def _handle_execution_result(self, message, sender=None):
        """Process execution result message."""
        self._log("debug", "Processing execution result from sender: " + str(sender))
        result = message.get("content", {})
        
        self.previous_execution_result = result.get("execution_result", "")
        self.execution_success = result.get("success", False)
        self.execution_code = result.get("code", "")
        self.is_auto_correction = result.get("is_auto_correction", False)
        self.is_timeout = result.get("is_timeout", False)
        
        # Move to processing results state
        if self.state == 'executing_code':
            self.execution_complete()
        
    def _handle_executor_error(self, message, sender=None):
        """Handle error messages from the Executor."""
        msg_type = message.get("type", "")
        error_message = message.get("content", "")
        
        self._log("info", f"Received {msg_type}: {error_message}")
        self.previous_execution_result = error_message
        self.error_type = msg_type
        
        if self.auto_fix_attempts >= self.max_auto_fix_attempts:
            self._log("info", "Max auto-correction attempts reached. Finishing review due to executor error.")
            self.finish_review()
            return
        
        self._log("info", f"Received {msg_type}, transitioning to reviewing_code for auto-correction.")
        self.auto_fix_attempts += 1
        
        # Use appropriate transition based on current state
        current_state = self.state
        self._log("debug", f"Current state before error handling: {current_state}")
        
        try:
            if current_state == 'idle':
                self.start_review()
                self.init_complete()
            elif current_state == 'initializing_review':
                self.init_complete()
            else:
                self.retry_review()
        except Exception as e:
            self._log("error", f"Error during state transition: {e}")
            # Emergency fallback - try to reset to a known state
            self._log("warning", "Using emergency transition to reviewing_code")
            # Force state change directly if transitions fail
            self.machine.set_state('reviewing_code')
            # Call the enter callback manually
            self.on_enter_reviewing_code()
            # If already in reviewing_code, the state machine will handle it
        
    def _handle_execution_success(self, message, sender=None):
        """Handle execution success message."""
        self._log("info", "Received execution_success message from Executor.")
        self.finish_review()
        
    def _handle_agent_stopped(self, message, sender=None):
        """Handle agent stopped message."""
        if sender == "CoderAgent":
            self._log("info", "Received agent_stopped from CoderAgent, stopping Reviewer.")
            self.finish_review()
            
    def receive_message(self, sender: str, message: Any):
        """Process incoming messages by delegating to the appropriate handler."""
        msg_type = message.get("type", "")
        self._log("debug", f"Received message from {sender}, type: {msg_type}, current state: {self.state}")
        
        self._log_dialogue(f"Received message from {sender}, type: {msg_type}, content: {message.get('content', 'N/A')}, dff_analysis: {message.get('dff_analysis', 'N/A')}")
        
        if self.state == 'complete':
            self._log("info", f"Review is complete, ignoring message type: {msg_type} from {sender}")
            return
            
        # Use the base class implementation for handler delegation
        super().receive_message(sender, message)