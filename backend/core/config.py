from pathlib import Path
from typing import Any

# 项目根目录
ROOT = Path(__file__).parent.parent

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.file import load_toml
from utils.log import global_logger
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


class Config:
    """
    配置管理类

    访问格式：config["配置文件名.表名.键名"]
    例如：config["global.global.env"] 访问 global.toml 中 [global] 表的 env 键
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # 配置目录路径
        self.CONFIGS_DIR = ROOT / "configs"
        global_logger.info("config", f"配置目录: {self.CONFIGS_DIR}")
        # 确保配置目录存在
        if not self.CONFIGS_DIR.exists():
            self.CONFIGS_DIR.mkdir(parents=True)
            global_logger.info("config", f"创建配置目录: {self.CONFIGS_DIR}")

        # 加载所有配置文件
        self._configs = {}

        # 加载其他配置文件
        config_files = [f for f in self.CONFIGS_DIR.glob("*.toml")]
        if not config_files:
            global_logger.error("config", "未找到任何配置文件")
            raise FileNotFoundError("未找到任何配置文件")

        for config_file in config_files:
            config = load_toml(config_file)
            self._configs[config_file.stem] = config

        self._build_flat_configs()
        self._validate_prod_env()

        # 配置系统初始化完成后，更新日志配置
        global_logger.configure_from_config(self)

        self._initialized = True

    def _validate_prod_env(self):
        """生产环境配置安全校验"""
        env = self._flat_configs.get("global.global.env", "dev")
        if env != "prod":
            return

        missing_vars = []
        for key, value in self._flat_configs.items():
            if isinstance(value, str) and "${" in value and "}" in value:
                missing_vars.append(f"{key}: {value}")

        if missing_vars:
            error_msg = "生产环境(prod)缺少必要的环境变量配置：\n" + "\n".join(
                missing_vars
            )
            global_logger.critical("config", error_msg)
            raise ValueError(error_msg)

    def __getitem__(self, key):
        """
        字典式访问配置值

        访问模式：
        1. 直接访问表：config["global"] → 返回整个global配置文件内容
        2. 嵌套访问：config["global.global.env"] → 返回具体配置值

        Args:
            key (str): 配置键，格式为 "配置文件名.表名.键名"

        Returns:
            any: 配置值

        Raises:
            KeyError: 当配置键不存在时

        Example:
            env = config['global.global.env']
            app_name = config['global.global.APP_NAME']
        """
        if "." not in key:
            # 直接访问表
            return self._configs[key]

        # 预构建扁平化映射
        if not hasattr(self, "_flat_configs"):
            self._build_flat_configs()

        if key not in self._flat_configs:
            available_keys = list(self._flat_configs.keys())[:10]  # 显示前10个可用键
            raise KeyError(
                f"配置键 '{key}' 不存在。\n可用的配置键示例: {available_keys}..."
            )

        return self._flat_configs[key]

    def get(self, key, default=None):
        """
        安全的配置访问方法

        Args:
            key (str): 配置键，格式为 "配置文件名.表名.键名"
            default: 当配置键不存在时返回的默认值

        Returns:
            any: 配置值或默认值

        Example:
            env = config.get('global.global.env', 'development')
            port = config.get('global.global.PORT', 8000)
            # 当键不存在时不会报错，返回默认值

        说明:
            带点路径与 __getitem__ 一致，从扁平映射读取；无点路径仍表示「整份配置文件」。
        """
        if not isinstance(key, str):
            return default
        if "." not in key:
            return self._configs.get(key, default)
        if not hasattr(self, "_flat_configs"):
            self._build_flat_configs()
        return self._flat_configs.get(key, default)

    def get_table(
        self, table_name: str, default: dict[str, Any] = {}
    ) -> dict[str, Any]:
        """
        获取指定表的配置（推荐用于获取一整张表/节，返回字典）

        Args:
            table_name (str): 表名/节名（如 'global', 'database', 'email.sender'）
            default (dict): 当不存在该表时返回的默认值（默认为空字典）

        Returns:
            dict[str, Any]: 该表完整配置（字典类型），若表不存在则返回 default

        Examples:
            db_conf = config.get_table('database')
            email_sender = config.get_table('email.sender', {})
        """
        return self._configs.get(table_name, default)

    def get_match(self, part_key: str) -> dict[str, Any]:
        """
        根据键关键字，模糊匹配值

        Args:
            part_key: 键关键字

        Return:
            dict[str, Any]: 查找出的结果[完整键: 值]
        """
        if not hasattr(self, "_flat_configs"):
            self._build_flat_configs()
        return {k: v for k, v in self._flat_configs.items() if part_key in k}

    def _build_flat_configs(self):
        """
        构建扁平化配置映射 - 性能优化核心

        Example:
            输入：{'global': {'env': 'development', 'PORT': 8000}}
            输出：{'global.global.env': 'development', 'global.global.PORT': 8000}
        """
        self._flat_configs = {}
        for config_name, config_data in self._configs.items():
            self._flatten_dict(config_data, config_name)
        global_logger.info("config", "已完成配置扁平化")

    def _flatten_dict(self, data: dict, prefix: str = ""):
        """
        递归扁平化嵌套字典

        Example:
            输入: {'admin': {'default_admin_username': 'admin'}}
            过程:
            1. 遍历到 'admin' 键，值为字典
            2. 递归调用，prefix='admin'
            3. 在递归中处理 'default_admin_username'，值为字符串
            4. 生成键名: 'admin.admin.default_admin_username'
        """
        for key, value in data.items():
            # 构建完整的键名路径
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # 继续递归子字典
                self._flatten_dict(value, full_key)
            else:
                # 叶节点，添加到扁平化映射
                self._flat_configs[full_key] = value

    def _search_value(self, table: dict, keys: list[str]) -> Any:
        """
        递归搜索配置值

        注意：此方法现已不常用，主要用于兼容原有代码

        Args:
            table: 当前层的配置字典
            keys: 剩余的键路径列表

        Returns:
            any: 找到的配置值

        Raises:
            KeyError: 当键路径不存在时
        """
        if not keys:
            raise ValueError("键路径为空")

        if len(keys) == 1:
            if keys[0] not in table:
                raise KeyError(f"在表中未找到键 '{keys[0]}'。")
            return table[keys[0]]

        if keys[0] in table and isinstance(table[keys[0]], dict):
            return self._search_value(table[keys[0]], keys[1:])
        raise KeyError(f"在表中未找到键 '{keys[0]}'。")

    def keys(self):
        """
        获取所有可用的配置键

        Returns:
            dict_keys: 所有配置键的迭代器

        Example:
            # 查看所有配置键
            all_keys = list(config.keys())
            print(f"共有 {len(all_keys)} 个配置键")

            # 查找特定前缀的配置键
            global_keys = [k for k in config.keys() if k.startswith('global.')]
        """
        if not hasattr(self, "_flat_configs"):
            self._build_flat_configs()
        return self._flat_configs.keys()

    def items(self) -> list[tuple[Any, Any]]:
        """
        获取所有配置项

        Returns:
            list[tuple[Any, Any]]: 所有配置键值对的列表

        Example:
            # 遍历所有配置项
            for key, value in config.items():
                print(f"{key}: {value}")
        """
        if not hasattr(self, "_flat_configs"):
            self._build_flat_configs()
        return list(self._flat_configs.items())

    def get_config_info(self, key=None):
        """
        获取配置系统信息

        Args:
            key (str, optional): 要查询的配置键，默认为None

        Returns:
            dict: 配置信息字典

        Examples:
            # 获取整体配置信息
            info = config.get_config_info()
            print(f"配置文件: {info['config_files']}")
            print(f"配置键总数: {info['total_keys']}")

            # 获取特定键信息
            env_info = config.get_config_info('global.global.env')
            print(f"键名: {env_info['key']}")
            print(f"值: {env_info['value']}")
            print(f"类型: {env_info['type']}")

            # 错误处理和智能建议
            error_info = config.get_config_info('global.wrong_key')
            print(f"错误: {error_info['error']}")
            print(f"建议: {error_info['suggestions']}")
        """
        if key is None:
            # 返回所有配置信息
            return {
                "available_keys": list(self.keys()),
                "config_files": list(self._configs.keys()),
                "total_keys": len(list(self.keys())),
            }

        # 确保key是字符串
        if not isinstance(key, str):
            raise TypeError(f"键名必须是字符串类型，获得: {type(key)}")

        # 返回特定键的信息
        try:
            value = self[key]
            return {"key": key, "value": value, "type": type(value).__name__}
        except KeyError:
            # 提供相似键的建议
            all_keys = list(self.keys())
            suggestions = [
                k
                for k in all_keys
                if key.split(".")[-1] in k or any(part in k for part in key.split("."))
            ]
            return {
                "key": key,
                "error": f"配置键 '{key}' 不存在",
                "suggestions": suggestions[:5],  # 最多5个建议
            }

    def check_dirs(self):
        """
        检查并创建配置中声明的目录路径

        Example:
            # 在应用启动时调用
            config.check_dirs()
            # 系统会自动创建配置中定义的所有目录
        """
        for config_name, config in self._configs.items():
            global_logger.info("config", f"检查配置: {config_name}")
            self._check_dirs(config, config_name)

    def _check_dirs(self, a_dict: dict, prefix: str = "") -> None:
        """
        递归检查并创建目录

        目录识别规则：
        - 值类型必须是字符串
        - 键名必须包含 'dir' 字符串
        - 例如：'database_dir', 'user_data_dir', 'temp_files_dir'

        Args:
            a_dict: 要检查的配置字典
            prefix: 当前路径前缀（用于日志记录）

        Raises:
            路径创建失败会抛出异常
            成功的创建操作会记录到日志

        Example:
            输入配置：{'database_dir': '/path/to/db', 'other_key': 'value'}
            处理结果：
            1. 检查到 'database_dir' 键
            2. 确认值为字符串且包含 'dir'
            3. 检查路径是否存在
            4. 如果不存在，创建该目录
        """
        for key, value in a_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # 递归处理嵌套字典
                self._check_dirs(value, full_key)
            elif isinstance(value, str) and ("dir" in full_key):
                # 识别为目录配置，进行创建
                path = Path(value)
                if not path.exists():
                    path.mkdir(parents=True)
                    global_logger.info("config", f"创建目录: {path}")


# 创建全局配置实例
config = Config()


def setup_core(app: FastAPI):
    """
    配置FastAPI核心中间件 - 应用初始化函数

    功能说明：
    1. 为FastAPI应用添加CORS中间件
    2. 从配置中读取CORS设置
    3. 配置跨域访问策略

    配置依赖：
    - 需要配置：config.global.global.cors_origins
    - 该配置应为列表格式，包含允许的源地址

    CORS策略：
    - allow_origins: 允许的源地址列表
    - allow_credentials: 是否允许携带凭证
    - allow_methods: 允许的HTTP方法
    - allow_headers: 允许的请求头

    Args:
        app (FastAPI): FastAPI应用实例

    Example:
        from fastapi import FastAPI
        from core.config import setup_core

        app = FastAPI()
        setup_core(app)  # 配置CORS中间件

        # 现在应用支持跨域访问
        # 允许的源地址由 config.global.global.cors_origins 配置决定
    """
    # 代理请求头解析中间件，放在最外层，用于在 Nginx 等代理后获取真实 IP
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    # ============================================================
    # 生产环境 CORS 配置说明
    # ============================================================
    # 生产环境部署时，应替换下方开发环境的 CORS 配置为以下严格配置：
    #
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=cors_origins,          # 必须指定具体域名列表，禁止使用通配符 "*"
    #     allow_credentials=True,
    #     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 仅允许必要的 HTTP 方法
    #     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],  # 仅允许必要的请求头
    #     allow_origin_regex=None,             # 不使用正则匹配
    #     max_age=600,                         # 预检请求缓存 10 分钟
    # )
    #
    # 注意事项：
    # 1. CORS_ORIGINS 环境变量必须配置为具体的前端域名（逗号分隔）
    # 2. 不要使用 "*" 通配符，会导致 credentials 模式失效
    # 3. 确保 allow_headers 包含所有前端实际发送的自定义头
    # ============================================================

    # 解析 CORS origins
    cors_origins_raw = config["global.global.cors_origins"]
    if isinstance(cors_origins_raw, str):
        if "${CORS_ORIGINS}" in cors_origins_raw:
            # 开发环境如果未设置 CORS_ORIGINS，默认放行本地前端
            cors_origins = ["http://localhost:5173"]
        else:
            cors_origins = [
                origin.strip()
                for origin in cors_origins_raw.split(",")
                if origin.strip()
            ]
    else:
        cors_origins = cors_origins_raw

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(IntegrityError)
    async def _integrity_exception_handler(request: Request, exc: IntegrityError):
        global_logger.exception("database", f"数据完整性异常: {exc}")
        return JSONResponse(
            status_code=409,
            content={
                "code": 409,
                "message": "数据冲突或重复提交",
                "data": None,
                "meta": None,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def _sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """
        数据库异常统一处理。

        目标：
        - 统一记录可定位的错误日志；
        - 对外返回稳定、非敏感的信息，避免泄露内部细节（SQL、连接信息等）。
        """

        global_logger.exception("database", f"数据库异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "数据库服务异常，请稍后重试",
                "data": None,
                "meta": None,
            },
        )
