import logging
import sys
from typing import Optional
import traceback

class GlobalLogger:
    """全局单例日志器类"""
    _instance = None
    _logger = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, debug: bool = False, log_file: Optional[str] = None):
        # 防止重复初始化
        if GlobalLogger._initialized:
            return
            
        # 设置日志级别
        level = logging.DEBUG if debug else logging.INFO
        
        # 创建 logger 对象
        self._logger = logging.getLogger("GlobalLogger")
        self._logger.setLevel(level)

        # 避免重复添加处理器
        if self._logger.handlers:
            GlobalLogger._initialized = True
            return

        # 创建颜色格式器
        class ColorFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': '\033[97m',  # 白色
                'INFO': '\033[92m',   # 绿色
                'WARNING': '\033[93m',  # 黄色
                'ERROR': '\033[91m',   # 红色
                'CRITICAL': '\033[1;91m'  # 加粗红色
            }
            RESET = '\033[0m'

            def format(self, record):
                color = self.COLORS.get(record.levelname, self.RESET)
                message = super().format(record)
                return f"{color}{message}{self.RESET}"

        # 定义日志格式
        formatter = ColorFormatter(
            fmt='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # 创建文件处理器（如果指定了日志文件）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        GlobalLogger._initialized = True

    def _log(self, level: int, module_name: str, message: str):
        """内部日志记录方法"""
        # 临时更改 logger 名称以显示模块名
        original_name = self._logger.name
        self._logger.name = module_name
        self._logger.log(level, message)
        self._logger.name = original_name

    def debug(self, module_name: str, message: str):
        """记录 DEBUG 级别日志"""
        self._log(logging.DEBUG, module_name, message)

    def info(self, module_name: str, message: str):
        """记录 INFO 级别日志"""
        self._log(logging.INFO, module_name, message)

    def warning(self, module_name: str, message: str):
        """记录 WARNING 级别日志"""
        self._log(logging.WARNING, module_name, message)

    def error(self, module_name: str, message: str):
        """记录 ERROR 级别日志"""
        self._log(logging.ERROR, module_name, message)

    def critical(self, module_name: str, message: str):
        """记录 CRITICAL 级别日志"""
        self._log(logging.CRITICAL, module_name, message)

    def exception(self, module_name: str, message: str):
        """记录异常日志，自动包含堆栈跟踪"""
        self._log(logging.ERROR, module_name, f"{message}\n{traceback.format_exc()}")


# 全局日志器实例
global_logger = GlobalLogger()


def setup_logger(name: str, debug: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    初始化日志器，返回一个配置好的 logger 对象
    :param name: 日志器名称
    :param debug: 是否开启调试模式
    :param log_file: 输出日志文件的位置

    :return 配置好的Logger实例
    """
    # 创建 logger 对象，名称用类名
    logger = logging.getLogger(name)

    # 避免重复添加处理器（重要！防止日志重复输出）
    if logger.handlers:
        return logger  # 如果已配置过，直接返回

    # 设置日志级别：debug模式输出所有级别，否则只输出 INFO 及以上
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # 创建颜色格式器
    class ColorFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[97m',  # 白色
            'INFO': '\033[92m',  # 绿色
            'WARNING': '\033[93m',  # 黄色
            'ERROR': '\033[91m',  # 红色
            'CRITICAL': '\033[1;91m'  # 加粗红色
        }
        RESET = '\033[0m'

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            message = super().format(record)
            return f"{color}{message}{self.RESET}"

    # 定义日志格式
    formatter = ColorFormatter(
        fmt='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式
    )

    # 创建控制台处理器（输出到命令行）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)  # 应用格式
    logger.addHandler(console_handler)  # 添加处理器到 logger

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # 文件只记录INFO及以上
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger