import hashlib
import random
import string
        
from datetime import datetime
from typing import Union, Optional


class Generator:
    """生成工具类，用于生成各种唯一标识符和哈希值"""
    
    @staticmethod
    def generate_uid_hash(username: str, salt: Optional[str] = None) -> str:
        """生成唯一的用户ID哈希
        
        Args:
            username: 用户名
            salt: 盐值，可选，默认使用当前时间戳
            
        Returns:
            生成的唯一用户ID哈希值
        """
        if not salt:
            salt = datetime.now().isoformat()
        
        # 使用用户名和盐值生成哈希
        hash_input = f"{username}-{salt}".encode()
        return hashlib.sha256(hash_input).hexdigest()
    
    @staticmethod
    def generate_file_hash(file_content: Union[bytes, str]) -> str:
        """生成文件哈希值
        
        Args:
            file_content: 文件内容，可以是字节流或字符串
            
        Returns:
            生成的文件哈希值
        """
        if isinstance(file_content, str):
            file_content = file_content.encode()
        
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    async def generate_jid() -> str:
        """生成稿件编号：YYYYMMDD + 每日自增序号（4位，不足补0）

        使用 Redis INCR 实现每日自增计数器，键格式: jid:counter:YYYYMMDD。
        示例: 202512120001（2025年12月12日第1篇）

        Returns:
            生成的稿件编号，如 202512120001
        """
        from service.redis_service import redis_service

        today = datetime.now().strftime("%Y%m%d")
        redis_key = f"jid:counter:{today}"

        # Redis INCR 原子自增，首次调用自动创建键并返回 1
        count = await redis_service.client.incr(redis_key)

        # 设置键过期时间为 48 小时（保留一天缓冲）
        if count == 1:
            await redis_service.client.expire(redis_key, 172800)

        # 格式化序号：默认 4 位，超过 9999 自动扩展
        seq = str(count).zfill(4)
        return f"{today}{seq}"
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """生成验证码
        
        Args:
            length: 验证码长度，默认6位
            
        Returns:
            生成的验证码
        """
        import random
        import string
        
        # 生成包含数字和大写字母的验证码
        characters = string.digits + string.ascii_uppercase
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    def generate_random_string(length: int = 16, include_special: bool = False) -> str:
        """生成随机字符串
        
        Args:
            length: 字符串长度，默认16位
            include_special: 是否包含特殊字符，默认不包含
            
        Returns:
            生成的随机字符串
        """
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += string.punctuation
        
        return ''.join(random.choices(characters, k=length))

# 创建全局生成器实例
generator = Generator()
