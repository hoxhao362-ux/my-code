import hashlib
from datetime import datetime
from typing import Union, Optional

import numba

class Generator:
    """生成工具类，用于生成各种唯一标识符和哈希值"""
    
    @staticmethod
    @numba.jit(nopython=True)
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
    @numba.jit(nopython=True)
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
    @numba.jit(nopython=True)
    def generate_jid() -> str:
        """根据当前时间戳生成唯一的JID
        
        Returns:
            生成的唯一JID
        """
        # 时间戳，保留小数点后3位
        timestamp = int(datetime.now().timestamp() * 1000)
        return f"{timestamp}"
    
    @staticmethod
    @numba.jit(nopython=True)
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
    @numba.jit(nopython=True)
    def generate_random_string(length: int = 16, include_special: bool = False) -> str:
        """生成随机字符串
        
        Args:
            length: 字符串长度，默认16位
            include_special: 是否包含特殊字符，默认不包含
            
        Returns:
            生成的随机字符串
        """
        import random
        import string
        
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += string.punctuation
        
        return ''.join(random.choices(characters, k=length))

# 创建全局生成器实例
generator = Generator()
