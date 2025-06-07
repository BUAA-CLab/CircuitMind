import logging
from colorama import Fore, Style, init
import os

init(autoreset=True)

# 定义自定义日志级别 DIALOGUE
DIALOGUE_LOG_LEVEL = 15
logging.addLevelName(DIALOGUE_LOG_LEVEL, "DIALOGUE")

class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式器."""
    def format(self, record):
        log_colors = {
            'DEBUG': Fore.BLUE,
            'INFO': Fore.GREEN,
            'DIALOGUE': Fore.MAGENTA,  # 新增 DIALOGUE 颜色
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Style.BRIGHT,
        }
        color = log_colors.get(record.levelname, Fore.WHITE)
        
        # 保存原始级别名称，以便在格式化后恢复
        original_levelname = record.levelname
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        formatted_record = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = original_levelname
        
        return formatted_record

def setup_logger(name, log_file=None, level=logging.DEBUG):
    """配置并返回一个 Logger 实例."""
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 检查是否已经配置过这个 logger
    if hasattr(logger, '_configured') and logger._configured:
        return logger
    
    # 清理已有的处理器，防止重复添加
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        if hasattr(handler, 'close'):
            handler.close()
    
    # 设置日志级别
    logger.setLevel(level)
    
    # 设置 propagate 为 False，防止日志传播到父 logger
    logger.propagate = False

    # 创建统一的格式字符串 - 确保所有地方使用相同格式
    fmt_str = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    date_fmt = '%Y-%m-%d %H:%M:%S,%03d'
    
    # 创建格式化器
    formatter = logging.Formatter(fmt_str, datefmt=date_fmt)
    formatter.default_msec_format = '%s,%03d'

    # 创建控制台 Handler
    sh = logging.StreamHandler()
    sh.setFormatter(ColoredFormatter(fmt_str))
    logger.addHandler(sh)

    # 如果指定了日志文件，则创建文件 Handler
    if log_file:
        # 确保目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    # 标记这个 logger 已经配置过
    logger._configured = True
    
    return logger

def reset_logging_system():
    """
    重置整个日志系统，清除所有日志处理器和记录器，
    并设置基本配置确保一致的日志格式。
    """
    # 重置根日志记录器
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # 确保正确的日志级别
    
    # 移除所有处理器
    for handler in list(root.handlers):
        root.removeHandler(handler)
        if hasattr(handler, 'close'):
            handler.close()
    
    # 清理所有其他日志记录器
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            if hasattr(handler, 'close'):
                handler.close()
    
    # 设置根日志记录器的基本配置
    setup_logger('root')
    
    # 特别处理transitions库的日志记录器
    transitions_logger = logging.getLogger('transitions')
    transitions_logger.setLevel(logging.INFO)
    
    # 确保transitions日志使用与root相同的处理器
    root_logger = logging.getLogger('root')
    for handler in root_logger.handlers:
        handler_copy = handler.__class__()
        handler_copy.setFormatter(handler.formatter)
        transitions_logger.addHandler(handler_copy)
    
    # 确保transitions库的日志不会传播到根
    transitions_logger.propagate = False
    
    # 同样处理其他常见库的日志记录器
    for lib_logger_name in ['httpx', 'httpcore', 'openai', 'urllib3']:
        lib_logger = logging.getLogger(lib_logger_name)
        lib_logger.setLevel(logging.INFO)
        # 禁止传播到根记录器以避免重复日志
        lib_logger.propagate = False