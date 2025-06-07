# agents/summarizer.py
import os
from typing import Any, List, Dict
from mediator import Mediator, Agent
from colorama import Fore, Style, init
from openai import OpenAI
import json
from utils.logger import setup_logger
from src.config import get_config_manager

init(autoreset=True)

class Summarizer(Agent):
    def __init__(self, name: str, mediator: Mediator, config: Dict[str, Any]):
        super().__init__(name, mediator, config)
        self.logger = setup_logger("Summarizer")
        self._log("debug", "Summarizer initialized.")
        
        # Get configuration manager and agent config
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config("Summarizer")
        self.app_config = config
        
        # Get system message from new config system
        system_messages = config.agent_system_messages
        self.system_message = system_messages.get(
            "Summarizer", 
            "You are an experiment summarization assistant responsible for analyzing and summarizing the experimental process."
        )
        
        # Initialize OpenAI client with current model configuration
        model_config = self.config_manager.get_model_config()
        self.client = OpenAI(
            api_key=model_config.api_key, 
            base_url=model_config.base_url
        )
        
        # Initialize tracking variables
        self.errors = []
        self.fixes = []
        self.feedbacks = []
        self.all_messages = []  # 用于存储所有消息
        
        # Get output file path - use model-specific path
        model_name = self.config_manager.config.current_model
        self.output_file = f"./knowledge_base/Model-incrementment/{model_name}.json"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def _log(self, level: str, message: str):
        getattr(self.logger, level)(message)

    def append_error(self, error_msg: str):
        self.errors.append(error_msg)
        self.all_messages.append(f"[ERROR] {error_msg}")
        self._log("error", f"Recording error: {error_msg}")

    def append_fix(self, fix_msg: str):
        self.fixes.append(fix_msg)
        self.all_messages.append(f"[FIX] {fix_msg}")
        self._log("info", f"Recording fix: {fix_msg}")

    def append_feedback(self, feedback: str):
        self.feedbacks.append(feedback)
        self.all_messages.append(f"[FEEDBACK] {feedback}")
        self._log("info", f"Recording feedback: {feedback}")

    def append_message(self, msg: str):
        self.all_messages.append(msg)
        self._log("debug", f"Recording message: {msg}")

    def generate_summary(self) -> str:
        messages = [f" - {msg}" for msg in self.all_messages]
        all_messages_str = "\n".join(messages)
        prompt = f"""Please analyze the following experimental dialogue process and summarize the experiment's objectives, the main problems encountered, the attempts to solve them, and the final outcome.

Experimental dialogue process:
{all_messages_str}

Please summarize this experiment using concise and clear language.
"""
        try:
            model_config = self.config_manager.get_model_config()
            response = self.client.chat.completions.create(
                model=model_config.name,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            summary = response.choices[0].message.content.strip()
            self._log("info", "LLM summarization complete.")
            return summary
        except Exception as e:
            self._log("error", f"Error calling OpenAI API for summarization: {e}")
            return "Summarization failed."

    def append_common_error_fix(self, error_msg: str, fix_msg: str):
        """Record common errors and fixes to a knowledge base file."""
        common_errors_file = "./knowledge_base/common_errors.md"
        
        if not os.path.exists(os.path.dirname(common_errors_file)):
            os.makedirs(os.path.dirname(common_errors_file), exist_ok=True)
        try:
            with open(common_errors_file, "a", encoding="utf-8") as f:
                f.write(f"## Experiment\n")
                f.write(f"- **Error:** {error_msg}\n")
                f.write(f"- **Fix:** {fix_msg}\n\n")
            self._log("info", f"Common error and fix recorded in {common_errors_file}")
        except Exception as e:
            self._log("error", f"Failed to write to {common_errors_file}: {e}")

    def write_summary(self):
        """Write summary to the configured summary file."""
        summary_file = self.app_config.experiments.summary_file
        if not summary_file:
            self._log("warning", "No summary file configured")
            return
            
        lines = [
            "=== Experiment Summary ===",
            f"Final Result: {getattr(self, 'result', 'Unknown')}",
            f"Final Message: {getattr(self, 'final_msg', 'No final message')}",
            "",
            "---- All debug messages & process ----"
        ] + [f" - {msg}" for msg in self.all_messages]
        summary_str = "\n".join(lines) + "\n\n"
        
        try:
            with open(summary_file, "a", encoding='utf-8') as sf:
                sf.write(summary_str)
            self._log("info", f"Summarizer has written a brief summary to {summary_file}")
        except Exception as e:
            self._log("error", f"Error writing summary.txt: {e}")

    def write_llm_summary(self, summary: str):
        """Write LLM-generated summary to file."""
        summary_file = self.app_config.experiments.summary_file
        if not summary_file:
            self._log("warning", "No summary file configured")
            return
            
        try:
            llm_summary_file = os.path.join(os.path.dirname(summary_file), "llm_summary.txt")
            with open(llm_summary_file, "w", encoding='utf-8') as f:
                f.write("=== Experiment LLM Summary ===\n")
                f.write(summary)
                f.write("\n\n")
            self._log("info", f"Summarizer has written the LLM summary to {llm_summary_file}")
        except Exception as e:
            self._log("error", f"Error writing LLM summary file: {e}")

    def update_resolved_issues(self):
        """Update the resolved issues knowledge base."""
        if not self.errors or not self.fixes:
            return
            
        result = getattr(self, 'result', 'Unknown')
        lines = [f"\n## Experiment - {result}"]
        for idx, err in enumerate(self.errors):
            fix_text = self.fixes[idx] if idx < len(self.fixes) else "No fix recorded"
            lines.append(f"- Error: {err}\n  => Fix: {fix_text}")
        add_str = "\n".join(lines) + "\n"
        
        kb_path = os.path.join("knowledge_base", "resolved_issues.md")
        try:
            os.makedirs(os.path.dirname(kb_path), exist_ok=True)
            with open(kb_path, "a", encoding='utf-8') as kb:
                kb.write(add_str)
            self._log("info", f"Summarizer has appended the error-fix mapping to {kb_path}")
        except Exception as e:
            self._log("error", f"Error writing to resolved_issues.md: {e}")

    def receive_message(self, sender: str, message: Any):
        self._log("debug", f"Received message from {sender}: {message}")
        msg_type = message.get("type", "")

        if msg_type == "compilation_error":
            err_msg = message.get("content", "")
            self.append_error("Compilation Error: " + err_msg)
        elif msg_type == "simulation_error":
            err_msg = message.get("content", "")
            self.append_error("Simulation/Test Error: " + err_msg)
        elif msg_type == "code_feedback":
            fb = message.get("content", {})
            if fb.get("needs_revision", False):
                self.append_feedback("Reviewer: " + fb.get("feedback", ""))
        elif msg_type == "fix_info":
            fix_str = message.get("content", "")
            self.append_fix(fix_str)
        elif msg_type == "execution_result":
            content = message.get("content", "")
            self.append_message("[EXECUTION_RESULT] " + content)
            if "All tests passed" in content:
                self.finalize(True, content)
        elif msg_type == "final_failure":
            fail_str = message.get("content", "")
            self.finalize(False, fail_str)
        elif msg_type == "execution_success":
            content = message.get("content", {})
            if isinstance(content, dict):
                code = content.get("code", "")
                exec_result = content.get("execution_result", "")
                design_requirements = content.get("design_requirements", "Unknown design requirements")
                self.append_message(f"[EXECUTION_SUCCESS] Code executed successfully:\n{exec_result}")
                self.finalize(True, code, exec_result, design_requirements)
            else:
                self._log("warning", f"Unexpected content format: {content}")
                self.finalize(True, content)

    def finalize(self, success: bool, code: str, execution_result: str = None, design_requirements: str = "Unknown design requirements"):
        """Finalize the experiment and save results."""
        module_name = self._extract_module_name(code)

        # 构造总结字典
        summary_entry = {
            "design_type": "combinational",  # 可根据设计要求动态确定
            "module_name": module_name,
            "design_requirements": design_requirements,
            "solution_pattern": code,
            "is_successful": success,
            "design_features": self._generate_design_features(code, design_requirements),
            "tags": self._generate_tags(code, design_requirements)
        }

        # 保存到 JSON 文件
        self._save_to_json(summary_entry)

        # 输出到控制台
        self._print_summary(success, code, execution_result)

    def _extract_module_name(self, code: str) -> str:
        import re
        match = re.search(r"module\s+(\w+)", code)
        return match.group(1) if match else "unknown_module"

    def _generate_design_features(self, code: str, design_requirements: str) -> List[str]:
        """Generate design features based on code analysis."""
        features = []
        if "not " in code:
            features.append("Implements a NOT gate using a single NOT primitive")
        elif "and " in code:
            features.append("Implements an AND gate using a single AND primitive")
        elif "or " in code:
            features.append("Implements an OR gate using a single OR primitive")
        elif "xor " in code:
            features.append("Implements an XOR gate using a single XOR primitive")
        elif "nand " in code:
            features.append("Implements a NAND gate using a single NAND primitive")
        elif "nor " in code:
            features.append("Implements a NOR gate using a single NOR primitive")
        elif "xnor " in code:
            features.append("Implements an XNOR gate using a single XNOR primitive")

        return features

    def _generate_tags(self, code: str, design_requirements: str) -> List[str]:
        tags = ["gate", "input", "output", "combinational"]
        if "not " in code:
            tags.append("NOT")
        elif "and " in code:
            tags.append("AND")
        return tags

    def _save_to_json(self, entry: dict):
        # 获取新条目的 module_name
        new_module_name = entry.get("module_name", "unknown_module")

        # 检查文件是否存在
        if os.path.exists(self.output_file):
            with open(self.output_file, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]  # 如果文件内容不是列表，转换为列表
                except json.JSONDecodeError:
                    data = []  # 如果文件为空或格式错误，从空列表开始
        else:
            data = []

        # 检查是否已存在相同的 module_name
        for existing_entry in data:
            if existing_entry.get("module_name") == new_module_name:
                self._log("info", f"Module '{new_module_name}' already exists in {self.output_file}. Skipping save.")
                return  # 跳过保存操作

        # 如果没有重复的 module_name，则追加新条目
        data.append(entry)
        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=4)
        self._log("info", f"Summary for module '{new_module_name}' saved to {self.output_file}")

    def _print_summary(self, success: bool, code: str, execution_result: str):
        result = "success" if success else "failure"
        final_message = f"Execution successful with code:\n{code}"
        summary = f"=== Experiment Summary ===\nFinal Result: {result}\nFinal Message: {final_message}"
        if execution_result:
            summary += "\n\n---- All debug messages & process ----\n"
            for msg in self.all_messages:  # 修复：使用 self.all_messages 而不是 self.messages
                summary += f" - {msg}\n"
        self._log("info", summary)