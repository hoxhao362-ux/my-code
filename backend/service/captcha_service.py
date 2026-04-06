"""
验证码服务模块

处理图形验证码的生成、缓存与验证业务逻辑。
利用 Redis 存储验证码并设置自动过期，验证后自动销毁以防止重放攻击。
"""
import uuid
from typing import Tuple

from utils.log import global_logger
from utils.captcha_util import captcha_util
from service.redis_service import redis_service

class CaptchaService:
    """验证码服务类"""
    
    def __init__(self):
        """初始化服务，设置 Redis 键前缀和验证码过期时间"""
        self.redis_prefix = "captcha:image:"
        self.expire_seconds = 300  # 验证码有效期：5分钟（300秒）

    async def generate_captcha(self) -> Tuple[str, str]:
        """
        生成图片验证码并存入 Redis
        
        Returns:
            Tuple[str, str]: (请求ID, Base64格式图片数据)
            
        Raises:
            Exception: Redis 服务不可用或其他内部异常时抛出
        """
        try:
            # 1. 使用工具类异步生成验证码文本和图片 Base64 数据
            text, image_b64 = await captcha_util.generate()
            
            # 2. 生成全局唯一的请求ID（去掉连字符）
            req_id = str(uuid.uuid4()).replace("-", "")
            
            # 3. 将验证码文本存入 Redis，统一转为小写处理，方便忽略大小写匹配
            redis_key = f"{self.redis_prefix}{req_id}"
            
            if not redis_service.client:
                global_logger.error("Captcha", "生成验证码时发现 Redis 未连接，无法缓存验证码")
                raise Exception("Redis 服务不可用")
                
            await redis_service.client.setex(
                name=redis_key, 
                time=self.expire_seconds, 
                value=text.lower()
            )
            
            global_logger.debug("Captcha", f"图形验证码已生成并存入缓存: req_id={req_id}, expires={self.expire_seconds}s")
            
            return req_id, image_b64
            
        except Exception as e:
            global_logger.error("Captcha", f"生成验证码服务失败: {e}")
            raise

    async def verify_captcha(self, req_id: str, code: str) -> bool:
        """
        校验前端提交的图形验证码
        
        规则：
        1. 无论验证成功与否，一旦尝试验证即销毁缓存数据，保证一次性验证。
        2. 忽略大小写进行匹配。
        
        Args:
            req_id: 验证码对应的请求ID
            code: 用户输入的验证码文本
            
        Returns:
            bool: 验证是否通过，通过返回 True，否则返回 False
        """
        if not req_id or not code:
            return False
            
        try:
            redis_key = f"{self.redis_prefix}{req_id}"
            
            if not redis_service.client:
                global_logger.error("Captcha", "验证验证码时发现 Redis 未连接")
                return False
                
            # 1. 从 Redis 中获取真实的验证码
            real_code = await redis_service.client.get(redis_key)
            
            # 2. 如果存在记录，不论输入是否正确，验证完都立即销毁，防止暴力破解和重放攻击
            if real_code is not None:
                await redis_service.client.delete(redis_key)
            else:
                global_logger.debug("Captcha", f"验证码验证失败：请求ID不存在或已过期 req_id={req_id}")
                return False
                
            # 3. 比对用户输入与真实验证码（忽略大小写）
            is_valid = (real_code == code.lower())
            
            if is_valid:
                global_logger.debug("Captcha", f"图形验证码验证成功: req_id={req_id}")
            else:
                global_logger.debug("Captcha", f"图形验证码验证失败：输入不匹配 req_id={req_id}, input={code}, real={real_code}")
                
            return is_valid
            
        except Exception as e:
            global_logger.error("Captcha", f"图形验证码校验过程异常: {e}")
            return False


# 实例化全局单例对象
captcha_service = CaptchaService()
