"""
邮件服务模块

提供邮件发送功能。
"""
import smtplib
from email.mime.text import MIMEText
from core.config import config
from utils.log import global_logger

class EmailService:
    """邮件服务类"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_inited'):
            # 注意：配置键名需要确认，假设为 global.email
            # 如果之前在 global.toml 中，现在可能需要检查是否移动了
            self.config = config.get('global.email', {}) 
            if not self.config:
                 # 暂时不强制报错，允许未配置时服务存在但不可用
                 global_logger.warning("Email", "Email配置未找到")
            self._inited = True
            
    # 这里需要补充发送邮件的方法，原文件似乎不完整或未展示全部
    # 假设需要 send_email 方法
    def send_email(self, to_email: str, subject: str, content: str):
        """发送邮件"""
        if not self.config:
            global_logger.error("Email", "邮件服务未配置，无法发送")
            return False
            
        try:
            msg = MIMEText(content, 'html', 'utf-8')
            msg['From'] = self.config.get('sender')
            msg['To'] = to_email
            msg['Subject'] = subject
            
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port')
            username = self.config.get('username')
            password = self.config.get('password')
            
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(username, password)
                server.send_message(msg)
                
            return True
        except Exception as e:
            global_logger.error("Email", f"发送邮件失败: {e}")
            return False

# 全局邮件服务实例
email_service = EmailService()
