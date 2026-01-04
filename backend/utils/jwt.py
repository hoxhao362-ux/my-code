"""
JWT工具模块

该模块提供了JWT令牌生成、验证以及密码加密验证的功能，用于期刊平台的用户认证系统。
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import JWTError, jwt  # JWT库，用于生成和验证令牌
from passlib.context import CryptContext  # 密码加密库

from core.config import config

# 默认配置
SECRET_KEY = config.global_.secret_key  # JWT签名密钥，生产环境必须更换为安全的随机字符串
ALGORITHM = config.global_.algorithm  # JWT加密算法，这里使用HS256（HMAC-SHA256）
ACCESS_TOKEN_EXPIRE_MINUTES = config.global_.access_token_expire_minutes  # 访问令牌过期时间（分钟）
REFRESH_TOKEN_EXPIRE_DAYS = config.global_.refresh_token_expire_days  # 刷新令牌过期时间（天）

# 密码加密上下文
# schemes: 使用的加密算法，这里使用bcrypt
# deprecated: 自动处理过时的加密算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTUtil:
    """JWT工具类，提供令牌生成、验证和密码处理功能（纯静态工具类）"""

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
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
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 使用默认过期时间
        to_encode.update({"exp": expire})  # 添加过期时间到载荷
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 直接使用全局配置
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
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
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)  # 使用默认过期时间
        to_encode.update({"exp": expire})  # 添加过期时间到载荷
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 直接使用全局配置
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证令牌并返回载荷
        
        Args:
            token (str): 要验证的JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 令牌有效则返回解码后的载荷，无效则返回None
        """
        try:
            # 解码令牌，验证签名和过期时间
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:  # 捕获JWT相关错误
            return None

    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        """从令牌中获取用户信息
        
        Args:
            token (str): 包含用户信息的JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 提取的用户信息，包括uid、username、role、email等
        """
        payload = JWTUtil.verify_token(token)  # 调用静态方法验证令牌
        if payload:  # 令牌有效
            # 从载荷中提取用户信息
            return {
                "uid": payload.get("uid"),  # 用户ID
                "username": payload.get("username"),  # 用户名
                "role": payload.get("role"),  # 用户角色
                "email": payload.get("email")  # 用户邮箱
            }
        return None

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希加密
        
        Args:
            password (str): 原始密码
            
        Returns:
            str: 哈希后的密码
        """
        return pwd_context.hash(password)  # 使用bcrypt算法对密码进行哈希

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            plain_password (str): 原始密码
            hashed_password (str): 哈希后的密码
            
        Returns:
            bool: 密码匹配返回True，否则返回False
        """
        return pwd_context.verify(plain_password, hashed_password)  # 验证原始密码与哈希密码是否匹配

jwt_util = JWTUtil()