import sys
from pathlib import Path
from typing import Optional

from loguru import logger


class GlobalLogger:
    """
    基于 loguru 的全局单例日志器类

    兼容原有的 `logging` 实现接口，提供更强大的日志轮转和格式化功能，
    适合生产环境。配置从 global.toml 中获取。
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, debug: bool = False, log_file: Optional[str] = None):
        """
        初始化全局日志器。

        为避免循环依赖 (config 导入 log_logger, logger 又依赖 config)，
        在此初始化阶段仅进行最基础的控制台配置。文件日志输出在后续通过
        显式调用 `setup_from_config` 或依赖注入实现，或者在这里采取延迟读取。
        """
        if GlobalLogger._initialized:
            return

        # 移除 loguru 默认的处理器，以防重复输出
        logger.remove()

        # 基础格式：带有模块名(extra["module_name"])
        # 如果未传入 module_name，则默认为 "App"
        self._format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[module_name]}</cyan> - "
            "<level>{message}</level>"
        )

        # 添加控制台处理器（基础配置）
        # 此时还没有加载 config，所以使用传参 debug 或默认 INFO
        initial_level = "DEBUG" if debug else "INFO"

        logger.add(
            sys.stdout,
            format=self._format,
            level=initial_level,
            enqueue=True,  # 异步写入，提升性能
        )

        GlobalLogger._initialized = True

    def configure_from_config(self, config_obj):
        """
        在系统配置初始化完成后调用，将根据配置文件重新设置日志。

        Args:
            config_obj: core.config.Config 实例
        """
        # 重新移除所有处理器，使用配置文件设置
        logger.remove()

        # 从配置中读取日志参数
        log_level = config_obj.get("global.global.log_level", "INFO").upper()
        log_dir = config_obj.get("global.global.log_dir", "logs")
        log_rotation = config_obj.get("global.global.log_rotation", "100 MB")
        log_retention = config_obj.get("global.global.log_retention", "30 days")
        log_compression = config_obj.get("global.global.log_compression", "zip")

        # 确保日志目录存在
        log_path = Path(log_dir)
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)

        # 1. 重新添加控制台处理器
        logger.add(sys.stdout, format=self._format, level=log_level, enqueue=True)

        # 2. 添加文件处理器 (按级别分离日志或汇总，这里采用汇总+ERROR单独输出的方式)
        # 全局汇总日志
        app_log_file = log_path / "app_{time:YYYY-MM-DD}.log"
        logger.add(
            str(app_log_file),
            format=self._format,
            level=log_level,
            rotation=log_rotation,
            retention=log_retention,
            compression=log_compression if log_compression else None,
            encoding="utf-8",
            enqueue=True,
            backtrace=True,  # 异常时记录完整的本地变量
            diagnose=True,  # 记录错误原因
        )

        # 独立错误日志文件 (只记录 ERROR 及以上级别)
        error_log_file = log_path / "error_{time:YYYY-MM-DD}.log"
        logger.add(
            str(error_log_file),
            format=self._format,
            level="ERROR",
            rotation=log_rotation,
            retention=log_retention,
            compression=log_compression if log_compression else None,
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    def _log(self, level: str, module_name: str, message: str):
        """内部日志记录方法，通过 bind 注入 extra 参数实现模块名显示"""
        logger.bind(module_name=module_name).log(level, message)

    def debug(self, module_name: str, message: str):
        """记录 DEBUG 级别日志"""
        self._log("DEBUG", module_name, message)

    def info(self, module_name: str, message: str):
        """记录 INFO 级别日志"""
        self._log("INFO", module_name, message)

    def warning(self, module_name: str, message: str):
        """记录 WARNING 级别日志"""
        self._log("WARNING", module_name, message)

    def error(self, module_name: str, message: str):
        """记录 ERROR 级别日志"""
        self._log("ERROR", module_name, message)

    def critical(self, module_name: str, message: str):
        """记录 CRITICAL 级别日志"""
        self._log("CRITICAL", module_name, message)

    def exception(self, module_name: str, message: str):
        """记录异常日志，自动包含堆栈跟踪"""
        # loguru 的 logger.exception() 会自动提取 traceback
        logger.bind(module_name=module_name).exception(message)


# 全局日志器实例 (初始时仅配置控制台)
global_logger = GlobalLogger()


def setup_logger(name: str, debug: bool = False, log_file: Optional[str] = None):
    """
    为了兼容旧有代码可能调用 setup_logger 的情况，保留该接口。
    建议后续统一使用 global_logger 实例。
    """
    # loguru 无需单独返回实例，直接返回全局 logger 或包装好的 GlobalLogger 均可
    return global_logger
