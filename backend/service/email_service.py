"""
邮件服务模块

提供异步邮件发送功能。
基于 aiosmtplib 实现完全异步的邮件发送。
"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List

import aiosmtplib

from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger


class EmailService(BaseManagedService):
    """
    邮件服务类
    
    继承自 BaseManagedService，提供异步邮件发送能力。
    """

    def __init__(self):
        # 初始化父类，注册服务名为 'email'
        super().__init__("email")
        
        # 邮件配置
        self._smtp_server: str = ""
        self._smtp_port: int = 465
        self._username: str = ""
        self._password: str = ""
        self._sender: str = ""
        self._use_tls: bool = True
        
        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载邮件配置"""
        # 尝试从 email.toml 或 global.toml 读取配置
        email_config = config.get('email.email', {})
        if not email_config:
            email_config = config.get('global.email', {})
            
        if email_config:
            self._smtp_server = email_config.get('smtp_server', '')
            self._smtp_port = email_config.get('smtp_port', 465)
            self._username = email_config.get('username', '')
            self._password = email_config.get('password', '')
            self._sender = email_config.get('sender', self._username)
            self._use_tls = email_config.get('use_tls', True)
        else:
            global_logger.warning("Email", "Email 配置未找到")

    async def start(self):
        """
        启动邮件服务（实现 BaseManagedService 接口）
        
        验证邮件配置是否完整
        """
        if not self._smtp_server or not self._username:
            global_logger.warning("Email", "邮件服务配置不完整，服务可能无法正常工作")
        else:
            global_logger.info("Email", f"邮件服务已就绪: {self._smtp_server}:{self._smtp_port}")
        
        self._initialized = True

    async def stop(self):
        """
        停止邮件服务（实现 BaseManagedService 接口）
        
        邮件服务无需特殊关闭操作
        """
        self._initialized = False
        global_logger.info("Email", "邮件服务已停止")

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str,
        content_type: str = "html"
    ) -> bool:
        """
        异步发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型，'html' 或 'plain'
            
        Returns:
            bool: 发送是否成功
        """
        if not self._smtp_server or not self._username:
            global_logger.error("Email", "邮件服务未配置，无法发送")
            return False
            
        try:
            # 构建邮件
            msg = MIMEText(content, content_type, 'utf-8')
            msg['From'] = self._sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 使用 aiosmtplib 异步发送
            await aiosmtplib.send(
                msg,
                hostname=self._smtp_server,
                port=self._smtp_port,
                username=self._username,
                password=self._password,
                use_tls=self._use_tls
            )
            
            global_logger.info("Email", f"邮件发送成功: to={to_email}, subject={subject}")
            return True
            
        except aiosmtplib.SMTPException as e:
            global_logger.error("Email", f"SMTP 错误: {e}")
            return False
        except Exception as e:
            global_logger.error("Email", f"发送邮件失败: {e}")
            return False

    async def send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        content: str,
        attachments: Optional[List[tuple]] = None,
        content_type: str = "html"
    ) -> bool:
        """
        异步发送带附件的邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            attachments: 附件列表，每个元素为 (filename, content_bytes, mime_type) 元组
            content_type: 内容类型，'html' 或 'plain'
            
        Returns:
            bool: 发送是否成功
        """
        if not self._smtp_server or not self._username:
            global_logger.error("Email", "邮件服务未配置，无法发送")
            return False
            
        try:
            # 构建多部分邮件
            msg = MIMEMultipart()
            msg['From'] = self._sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 添加附件
            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                
                for filename, content_bytes, mime_type in attachments:
                    maintype, subtype = mime_type.split('/', 1)
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(content_bytes)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=filename
                    )
                    msg.attach(part)
            
            # 使用 aiosmtplib 异步发送
            await aiosmtplib.send(
                msg,
                hostname=self._smtp_server,
                port=self._smtp_port,
                username=self._username,
                password=self._password,
                use_tls=self._use_tls
            )
            
            global_logger.info("Email", f"带附件邮件发送成功: to={to_email}, subject={subject}")
            return True
            
        except aiosmtplib.SMTPException as e:
            global_logger.error("Email", f"SMTP 错误: {e}")
            return False
        except Exception as e:
            global_logger.error("Email", f"发送带附件邮件失败: {e}")
            return False

    async def send_batch_emails(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        content_type: str = "html"
    ) -> dict:
        """
        批量发送邮件
        
        Args:
            recipients: 收件人邮箱列表
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型
            
        Returns:
            dict: {"success": int, "failed": int, "failed_emails": list}
        """
        success = 0
        failed = 0
        failed_emails = []
        
        for email in recipients:
            if await self.send_email(email, subject, content, content_type):
                success += 1
            else:
                failed += 1
                failed_emails.append(email)
                
        return {
            "success": success,
            "failed": failed,
            "failed_emails": failed_emails
        }

    @property
    def is_configured(self) -> bool:
        """检查邮件服务是否已配置"""
        return bool(self._smtp_server and self._username)


# 全局邮件服务实例
email_service = EmailService()
