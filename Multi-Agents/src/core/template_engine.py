
# src/core/template_engine.py
from jinja2 import Environment, FileSystemLoader, Template, TemplateError as JinjaTemplateError
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from src.core.exceptions import TemplateError

class TemplateEngine:
    """模板引擎"""
    
    def __init__(self, template_dirs: list = None):
        """
        初始化模板引擎
        
        Args:
            template_dirs: 模板目录列表
        """
        if template_dirs is None:
            template_dirs = ["agents/prompts", "templates"]
        
        # 确保模板目录存在
        existing_dirs = []
        for template_dir in template_dirs:
            path = Path(template_dir)
            if path.exists():
                existing_dirs.append(str(path))
        
        if not existing_dirs:
            # 创建默认模板目录
            default_dir = Path("templates")
            default_dir.mkdir(exist_ok=True)
            existing_dirs = [str(default_dir)]
        
        self.env = Environment(
            loader=FileSystemLoader(existing_dirs),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        self.logger = logging.getLogger(__name__)
        
        # 注册自定义过滤器
        self._register_filters()
    
    def _register_filters(self):
        """注册自定义过滤器"""
        
        def format_code(text):
            """格式化代码"""
            if not text:
                return ""
            lines = text.strip().split('\n')
            # 移除空行
            lines = [line for line in lines if line.strip()]
            return '\n'.join(lines)
        
        def truncate_smart(text, length=100):
            """智能截断文本"""
            if not text or len(text) <= length:
                return text
            return text[:length-3] + "..."
        
        self.env.filters['format_code'] = format_code
        self.env.filters['truncate_smart'] = truncate_smart
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板名称
            context: 模板上下文
            
        Returns:
            渲染后的字符串
        """
        if context is None:
            context = {}
        
        try:
            template = self.env.get_template(template_name)
            result = template.render(context)
            self.logger.debug(f"Rendered template {template_name}")
            return result
        except JinjaTemplateError as e:
            error_msg = f"Template error in {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error rendering template {template_name}: {e}"
            self.logger.error(error_msg)
            raise TemplateError(error_msg) from e
    
    def render_string(self, template_str: str, context: Dict[str, Any] = None) -> str:
        """
        渲染字符串模板
        
        Args:
            template_str: 模板字符串
            context: 模板上下文
            
        Returns:
            渲染后的字符串
        """
        if context is None:
            context = {}
        
        try:
            template = Template(template_str, environment=self.env)
            result = template.render(context)
            self.logger.debug("Rendered string template")
            return result
        except JinjaTemplateError as e:
            error_msg = f"Template error in string template: {e}"
            self.logger.error(error_msg)
            raise TemplateError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error rendering string template: {e}"
            self.logger.error(error_msg)
            raise TemplateError(error_msg) from e
    
    def template_exists(self, template_name: str) -> bool:
        """检查模板是否存在"""
        try:
            self.env.get_template(template_name)
            return True
        except JinjaTemplateError:
            return False
    
    def list_templates(self) -> list:
        """列出所有可用的模板"""
        return self.env.list_templates()


