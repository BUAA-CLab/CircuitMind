# utils/utils.py

import re

##############################################################################
# 工具函数：提取 Verilog 代码块、提取模块名
##############################################################################

def extract_code_blocks(text: str) -> list:
    """
    从文本中提取所有 Verilog 代码块内容（```verilog ... ```）。
    """
    pattern = re.compile(r"```verilog\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
    return pattern.findall(text)

def extract_module_name(verilog_code: str) -> str:
    """
    从 Verilog 代码中提取第一个 module 名。
    未找到则返回 "design"。
    """
    match = re.search(r'\bmodule\s+(\w+)', verilog_code)
    if match:
        return match.group(1)
    return "design"
def clean_code_block(code_block):
    # 使用正则表达式匹配 <| xxx |> 模式，并替换为空字符串
    cleaned_code = re.sub(r'<\|.*?\|>', '', code_block)
    return cleaned_code