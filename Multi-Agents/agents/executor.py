# executor.py

import os
import re
from subprocess import Popen, PIPE
from typing import Any, Dict, List, Tuple
from agent_base import BaseAgent
from mediator import Mediator
from utils.logger import setup_logger, DIALOGUE_LOG_LEVEL
from colorama import Fore, Style, init
from src.config import get_config_manager

init(autoreset=True)

class Executor(BaseAgent):
    """
    Agent responsible for compiling and executing Verilog code,
    reporting results to other agents in the system.
    """
    
    def __init__(self, name: str, mediator: Mediator, config):
        """
        Initialize the Executor agent.
        
        Args:
            name: Agent name
            mediator: Mediator for agent communication
            config: Application configuration from new config system
        """
        super().__init__(name, mediator, config, role="executor")
        
        # Get configuration manager and agent config
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config("Executor")
        self.app_config = config
        
        # Register message handlers
        self.register_message_handler(self.MSG_TYPE_VERILOG_CODE, self._handle_verilog_code)
        
        # Initialize agent-specific attributes using new config
        self.retry_count = 0
        self.expecting_review_feedback = False
        self.current_code = ""
        self.max_retry_attempts = self.agent_config.max_retry_attempts
        
        # Get timeout from agent config if available, otherwise use default
        timeout_val = getattr(self.agent_config, 'timeout', 2)
        self.timeout = timeout_val if timeout_val is not None else 2
    
    def compile_and_simulate(self, verilog_file: str, testbench_file: str, reference_file: str, project_path: str) -> Tuple[bool, str, bool, bool]:
        """
        Compile and simulate Verilog code.
        
        Args:
            verilog_file: Path to the Verilog source file
            testbench_file: Path to the testbench file
            reference_file: Path to the reference file
            project_path: Path to the project directory
            
        Returns:
            Tuple containing:
            - Success flag (bool)
            - Output message (str)
            - Timeout flag (bool)
            - Compilation error flag (bool)
        """
        # Compile the Verilog code
        compile_cmd = f"iverilog -o {project_path}/output.vvp {verilog_file} {testbench_file} {reference_file}"
        self._log_dialogue(f"Compilation command: {compile_cmd}")
        
        proc = Popen(compile_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        
        if proc.returncode != 0:
            self._log_dialogue(f"Compilation failed.\nSTDOUT:\n{out.decode()}\nSTDERR:\n{err.decode()}")
            return False, err.decode(), False, True

        # Run the simulation with a timeout
        timeout_sec = self.timeout
        run_cmd = f"timeout {timeout_sec}s vvp {project_path}/output.vvp"
        self._log_dialogue(f"Run command (with timeout): {run_cmd}")
        
        proc2 = Popen(run_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out2, err2 = proc2.communicate()

        stdout_output = out2.decode()
        stderr_output = err2.decode()

        # Handle different simulation outcomes
        if proc2.returncode == 124:  # Timeout code
            error_message = f"Simulation timed out after {timeout_sec} seconds."
            self._log_dialogue(f"{error_message}\nSTDOUT:\n{stdout_output}\nSTDERR:\n{stderr_output}")
            return False, error_message, True, False
        elif proc2.returncode != 0:
            self._log_dialogue(f"Simulation failed.\nSTDOUT:\n{stdout_output}\nSTDERR:\n{stderr_output}")
            return False, stderr_output, False, False

        self._log_dialogue(f"Simulation successful.\nSTDOUT:\n{stdout_output}")
        return True, stdout_output, False, False
    
    def extract_module_name(self, code: str) -> str:
        """Extract the module name from Verilog code."""
        match = re.search(r"module\s+(\w+)", code)
        return match.group(1) if match else "unknown_module"
    
    def _handle_verilog_code(self, message, sender=None):
        """Handle a Verilog code message."""
        if self.retry_count > self.max_retry_attempts:
            self._log("error", "Exceeded maximum retry attempts. Ignoring message.")
            return

        self._log("info", "Executor starting Verilog execution.")
        
        # Extract and clean the code
        code = message.get("content", "")
        is_auto_correction = message.get("is_auto_correction", False)
        code = re.sub(r'^\s*```\s*verilog\s*|^\s*```\s*|^\s*```|```\s*$', '', code, flags=re.MULTILINE).strip()
        self.current_code = code

        # Save the Verilog file
        module_name = self.extract_module_name(code)
        base_file_name = f"{module_name}.v"
        
        # Get project path from experiment config
        project_path = self.app_config.experiments.verilog_dir
        if not project_path:
            self._log("error", "Verilog directory not configured")
            return
            
        os.makedirs(project_path, exist_ok=True)
        verilog_file_path = os.path.join(project_path, base_file_name)

        # Create a unique filename if the file already exists
        if os.path.exists(verilog_file_path):
            index = 1
            while True:
                new_file_name = f"{module_name}_{index}.v"
                verilog_file_path = os.path.join(project_path, new_file_name)
                if not os.path.exists(verilog_file_path):
                    break
                index += 1

        # Write the code to the file
        with open(verilog_file_path, "w") as vf:
            vf.write(code)

        self._log("info", f"Verilog code saved to: {verilog_file_path}")

        # Get the testbench and reference files from experiment config
        testbench_file = self.app_config.experiments.testbench_path
        reference_file = self.app_config.experiments.reference_code_path

        # Check if the files exist
        if not testbench_file or not os.path.exists(testbench_file):
            err_str = f"Testbench file not found: {testbench_file}"
            self._log("error", err_str)
            self.send_message(["UserProxy"], {"type": "execution_result", "content": err_str})
            return

        if not reference_file or not os.path.exists(reference_file):
            err_str = f"Reference Code file not found: {reference_file}"
            self._log("error", err_str)
            self.send_message(["UserProxy"], {"type": "execution_result", "content": err_str})
            return

        # Compile and simulate the code
        success, output, is_timeout, is_compilation_error = self.compile_and_simulate(
            verilog_file_path, testbench_file, reference_file, project_path
        )
        self.expecting_review_feedback = True

        # Handle different outcomes based on success and auto-correction
        if success:
            if is_auto_correction:
                if "All tests passed" in output:
                    self._log("info", "Tests passed, and auto correction success.")
                    self.send_message(["Reviewer"], {
                        "type": "execution_success",
                        "content": {
                            "code": code,
                            "execution_result": output
                        }
                    })
                    self.expecting_review_feedback = False
                else:
                    self._log("info", "Tests failed, and auto correction failed, sending to Reviewer for feedback.")
                    if self.expecting_review_feedback:
                        self.send_message(["Reviewer"], {
                            "type": "execution_result_and_code",
                            "content": {
                                "execution_result": output,
                                "code": code,
                                "success": success,
                                "is_auto_correction": True,
                                "is_timeout": is_timeout
                            }
                        })
                        self.expecting_review_feedback = False
            else:
                if "All tests passed" in output:
                    self._log("info", "Tests passed, pending Reviewer's approval.")
                    if self.expecting_review_feedback:
                        self.send_message(["Reviewer"], {
                            "type": "execution_result_and_code",
                            "content": {
                                "execution_result": output,
                                "code": code,
                                "success": success,
                                "is_auto_correction": False,
                                "is_timeout": is_timeout
                            }
                        })
                        self.expecting_review_feedback = False
                else:
                    self._log("info", "Tests failed, sending to Reviewer for feedback.")
                    if self.expecting_review_feedback:
                        self.send_message(["Reviewer"], {
                            "type": "execution_result_and_code",
                            "content": {
                                "execution_result": output,
                                "code": code,
                                "success": success,
                                "is_auto_correction": False,
                                "is_timeout": is_timeout
                            }
                        })
                        self.expecting_review_feedback = False
        else:
            self._log("error", f"Compilation/simulation failed: {output}")
            if is_timeout:
                if self.expecting_review_feedback:
                    self.send_message(["Reviewer"], {"type": "simulation_error", "content": output})
                    self.expecting_review_feedback = False
            else:
                self.increment_retry()
                if self.expecting_review_feedback:
                    self.send_message(["Reviewer"], {
                        "type": "compilation_error" if is_compilation_error else "simulation_error", 
                        "content": output
                    })
                    self.expecting_review_feedback = False
    
    def increment_retry(self):
        """Increment the retry counter and check if maximum is reached."""
        self.retry_count += 1
        if self.retry_count > self.max_retry_attempts:
            self._log("error", "Exceeded maximum retry attempts.")
            self.send_message(["UserProxy"], {"type": "execution_failed", "content": "Exceeded maximum retry attempts."})
    
    def reset_retry(self):
        """Reset the retry counter."""
        self.retry_count = 0