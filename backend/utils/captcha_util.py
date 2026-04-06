"""
验证码工具模块

提供基于 captcha 库的图片验证码生成功能。
因为 captcha 库的验证码生成是 CPU 密集型操作，
为避免阻塞异步环境中的事件循环，推荐使用异步方法生成。
"""
import random
import string
import base64
import asyncio
import io
from captcha.image import ImageCaptcha


class CaptchaUtil:
    """验证码生成工具类"""
    
    def __init__(self, width: int = 160, height: int = 60, length: int = 4):
        """
        初始化验证码生成工具
        
        Args:
            width: 图片宽度
            height: 图片高度
            length: 验证码字符长度
        """
        self.width = width
        self.height = height
        self.length = length
        
        # 预先实例化 ImageCaptcha，可以复用以提高性能
        self.image_captcha = ImageCaptcha(width=self.width, height=self.height)
        
        # 去除容易混淆的字符（如：0, O, 1, I, l 等），使用去混淆的字符集
        self.charset = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz"

    def generate_sync(self) -> tuple[str, str]:
        """
        同步生成验证码
        
        Returns:
            tuple[str, str]: (验证码文本, 验证码图片的 Base64 编码数据)
        """
        # 1. 随机生成验证码文本
        captcha_text = ''.join(random.choices(self.charset, k=self.length))
        
        # 2. 生成验证码图片，返回 io.BytesIO
        data: io.BytesIO = self.image_captcha.generate(captcha_text)
        
        # 3. 将图片数据转换为 base64 字符串
        base64_img = base64.b64encode(data.getvalue()).decode('utf-8')
        
        # 4. 拼接成可以直接在前端 img 标签 src 属性中使用的 Data URL 格式
        image_data_url = f"data:image/png;base64,{base64_img}"
        
        return captcha_text, image_data_url

    async def generate(self) -> tuple[str, str]:
        """
        异步生成验证码
        
        使用 asyncio.to_thread 在独立线程中执行同步的 CPU 密集型生成过程，
        避免阻塞主事件循环，提升异步并发性能。
        
        Returns:
            tuple[str, str]: (验证码文本, 验证码图片的 Base64 编码数据)
        """
        return await asyncio.to_thread(self.generate_sync)


# 实例化全局工具对象
captcha_util = CaptchaUtil()
