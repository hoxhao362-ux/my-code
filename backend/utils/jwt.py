"""
JWT工具模块

该模块提供了JWT令牌生成、验证以及密码加密验证的功能，用于期刊平台的用户认证系统。
支持基于Redis的JWT密钥轮换机制。
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt  # 密码加密库
from core.config import config
from jose import JWTError, jwt  # JWT库，用于生成和验证令牌
from utils.log import global_logger

# 延迟导入 redis_service，避免循环导入
_redis_service = None


def _get_redis_service():
    """延迟获取 Redis 服务实例"""
    global _redis_service
    if _redis_service is None:
        from service.redis_service import redis_service

        _redis_service = redis_service
    return _redis_service


# 默认配置（从配置文件读取，仅作为初始值）
ALGORITHM = config[
    "global.global.algorithm"
]  # JWT加密算法，这里使用HS256（HMAC-SHA256）
ACCESS_TOKEN_EXPIRE_MINUTES = config[
    "global.global.access_token_expire_minutes"
]  # 访问令牌过期时间（分钟）
REFRESH_TOKEN_EXPIRE_DAYS = config[
    "global.global.refresh_token_expire_days"
]  # 刷新令牌过期时间（天）

# bcrypt 密码哈希配置
# bcrypt 限制密码最大 72 字节，超过将被截断
BCRYPT_MAX_PASSWORD_BYTES = 72


def _get_password_salt() -> str:
    """从配置获取密码盐值"""
    return config.get("global.global.salt", "")


def _apply_salt_to_password(password: str) -> bytes:
    """
    对密码应用盐值处理

    处理流程: SHA256(salt + password) → 截断到 72 字节
    注意：前端传入的 password 已经是 SHA256(原始密码) 的哈希值
    后端处理: SHA256(salt + 前端SHA256哈希) → bcrypt

    Args:
        password: 前端传入的密码（已进行 SHA256 哈希）

    Returns:
        bytes: 处理后的密码字节（已截断到 72 字节）
    """
    salt = _get_password_salt()
    # 拼接 salt + password，然后做 SHA256
    salted = salt + password
    hashed = hashlib.sha256(salted.encode("utf-8")).hexdigest()
    # 截断到 72 字节以适应 bcrypt 限制
    return hashed.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


class JWTUtil:
    """JWT工具类，提供令牌生成、验证和密码处理功能（纯静态工具类）"""

    @staticmethod
    async def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """生成访问令牌

        Args:
            data (Dict[str, Any]): 要包含在令牌中的数据（载荷）
            expires_delta (Optional[timedelta]): 自定义过期时间

        Returns:
            str: 生成的JWT访问令牌
        """
        to_encode = data.copy()  # 复制数据，避免修改原始数据
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta  # 使用自定义过期时间
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )  # 使用默认过期时间
        to_encode.update({"exp": expire})  # 添加过期时间到载荷

        # 从 Redis 获取当前密钥
        redis_svc = _get_redis_service()
        secret_key = await redis_svc.get_current_jwt_key()

        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        global_logger.debug("JWTUtil", f"已生成访问令牌 - uid: {data.get('uid')}")
        return encoded_jwt

    @staticmethod
    async def create_refresh_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """生成刷新令牌

        Args:
            data (Dict[str, Any]): 要包含在令牌中的数据（载荷）
            expires_delta (Optional[timedelta]): 自定义过期时间

        Returns:
            str: 生成的JWT刷新令牌
        """
        to_encode = data.copy()  # 复制数据，避免修改原始数据
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta  # 使用自定义过期时间
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )  # 使用默认过期时间
        to_encode.update({"exp": expire})  # 添加过期时间到载荷

        # 从 Redis 获取当前密钥
        redis_svc = _get_redis_service()
        secret_key = await redis_svc.get_current_jwt_key()

        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        global_logger.debug("JWTUtil", f"已生成刷新令牌 - uid: {data.get('uid')}")
        return encoded_jwt

    @staticmethod
    async def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证令牌并返回载荷

        先用当前密钥验证，失败后尝试使用上一代密钥（过渡期兼容）

        Args:
            token (str): 要验证的JWT令牌

        Returns:
            Optional[Dict[str, Any]]: 令牌有效则返回解码后的载荷，无效则返回None
        """
        redis_svc = _get_redis_service()

        # 首先尝试使用当前密钥验证
        try:
            current_key = await redis_svc.get_current_jwt_key()
            payload = jwt.decode(token, current_key, algorithms=[ALGORITHM])
            global_logger.debug("JWTUtil", "令牌验证成功（使用当前密钥）")
            return payload
        except JWTError:
            # 当前密钥验证失败，尝试上一代密钥
            pass

        # 尝试使用上一代密钥验证（过渡期兼容）
        try:
            previous_key = await redis_svc.get_previous_jwt_key()
            if previous_key:
                payload = jwt.decode(token, previous_key, algorithms=[ALGORITHM])
                global_logger.debug("JWTUtil", "令牌验证成功（使用上一代密钥）")
                return payload
        except JWTError:
            # 上一代密钥也验证失败
            pass

        global_logger.debug("JWTUtil", "令牌验证失败")
        return None

    @staticmethod
    async def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """从令牌中获取用户信息

        Args:
            token (str): 包含用户信息的JWT令牌

        Returns:
            Optional[Dict[str, Any]]: 提取的用户信息，包括uid、username、role、email等
        """
        payload = await JWTUtil.verify_token(token)  # 调用异步方法验证令牌
        if payload:  # 令牌有效
            # 从载荷中提取用户信息
            return {
                "uid": payload.get("uid"),  # 用户ID
                "username": payload.get("username"),  # 用户名
                "role": payload.get("role"),  # 用户角色
                "email": payload.get("email"),  # 用户邮箱
            }
        return None

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希加密

        使用 bcrypt 算法对密码进行哈希，并加入 salt 增强安全性。
        处理流程: SHA256(salt + 前端SHA256哈希) → bcrypt

        Args:
            password: 前端传入的密码（已进行 SHA256 哈希）

        Returns:
            str: 哈希后的密码
        """
        # 对密码应用盐值处理
        password_bytes = _apply_salt_to_password(password)
        # 生成盐并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # 返回字符串形式的哈希值
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码

        验证原始密码与哈希密码是否匹配。
        处理流程: SHA256(salt + 前端SHA256哈希) → bcrypt 验证

        Args:
            plain_password: 前端传入的密码（已进行 SHA256 哈希）
            hashed_password: 哈希后的密码

        Returns:
            bool: 密码匹配返回True，否则返回False
        """
        try:
            # 对密码应用盐值处理
            password_bytes = _apply_salt_to_password(plain_password)
            hashed_bytes = hashed_password.encode("utf-8")
            # 验证密码
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # 如果哈希值格式无效，返回 False
            return False


jwt_util = JWTUtil()
