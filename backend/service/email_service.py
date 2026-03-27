"""
邮件服务模块

提供异步邮件发送功能。
基于 aiosmtplib 实现完全异步的邮件发送。
支持验证码邮件、自定义模板邮件等生产级功能。
"""
import re
import random
import string
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any

import aiosmtplib

from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger


class EmailService(BaseManagedService):
    """
    邮件服务类
    
    继承自 BaseManagedService，提供异步邮件发送能力。
    支持：
    - 基础邮件发送（HTML/纯文本）
    - 带附件邮件发送
    - 批量邮件发送
    - 验证码邮件发送
    - 自定义模板邮件渲染和发送
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
        
        # 验证码配置
        self._code_length: int = 6
        self._code_expire_minutes: int = 5
        
        # 模板缓存
        self._template_cache: Dict[str, Dict[str, str]] = {}
        
        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载邮件配置"""
        # 尝试从 email.toml 读取配置
        sender_config = config.get('email.sender', {})
        code_config = config.get('email.code', {})
        
        if sender_config:
            self._smtp_server = sender_config.get('smtp_server', '')
            # 端口可能是字符串，转换为整数
            port_value = sender_config.get('smtp_port', 465)
            try:
                self._smtp_port = int(port_value)
            except (ValueError, TypeError):
                self._smtp_port = 465
            # 支持两种配置键名
            self._username = sender_config.get('sender_email', sender_config.get('username', ''))
            self._password = sender_config.get('sender_auth_code', sender_config.get('password', ''))
            self._sender = sender_config.get('sender_email', self._username)
            self._use_tls = sender_config.get('use_tls', True)
        else:
            # 尝试从 global.email 读取
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
        
        # 加载验证码配置
        if code_config:
            self._code_length = code_config.get('code_length', 6)
            self._code_expire_minutes = code_config.get('code_expire_minutes', 5)
        
        # 预加载邮件模板
        self._load_templates()
    
    def _load_templates(self):
        """预加载邮件模板到缓存"""
        template_sections = ['email.verify_email', 'email.reset_password', 
                            'email.invite_reviewer', 'email.custom']
        
        for section in template_sections:
            templates = config.get(section, {})
            if templates:
                for key, value in templates.items():
                    if isinstance(value, dict) and 'title' in value and 'content' in value:
                        self._template_cache[f"{section}.{key}"] = value
                        
        global_logger.info("Email", f"已加载 {len(self._template_cache)} 个邮件模板")

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
    
    # ==================== 验证码相关方法 ====================
    
    def generate_verification_code(self, length: Optional[int] = None) -> str:
        """
        生成数字验证码
        
        Args:
            length: 验证码长度，默认使用配置值
            
        Returns:
            str: 数字验证码
        """
        length = length or self._code_length
        return ''.join(random.choices(string.digits, k=length))
    
    async def send_verification_email(
        self, 
        to_email: str, 
        code_type: str = "verify_email",
        code: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code_type: 验证码类型 ('verify_email' | 'reset_password')
            code: 可选，指定验证码，否则自动生成
            
        Returns:
            tuple: (发送是否成功, 验证码)
        """
        if not self.is_configured:
            global_logger.error("Email", "邮件服务未配置，无法发送验证码")
            return False, None
        
        # 生成或获取验证码
        verification_code = code or self.generate_verification_code()
        
        # 获取模板配置
        template_key = f"email.{code_type}"
        template = config.get(template_key, {})
        
        if not template:
            global_logger.error("Email", f"未找到验证码模板: {template_key}")
            return False, None
        
        subject = template.get('title', 'Verification Code')
        content_template = template.get('content', 'Your code is: {}')
        
        # 格式化内容
        try:
            content = content_template.format(verification_code, self._code_expire_minutes)
        except Exception:
            # 如果模板只期望一个参数
            content = content_template.format(verification_code)
        
        # 发送邮件
        success = await self.send_email(to_email, subject, content, content_type="plain")
        
        if success:
            global_logger.info("Email", f"验证码邮件发送成功: to={to_email}, type={code_type}")
            return True, verification_code
        else:
            return False, None
    
    # ==================== 模板邮件方法 ====================
    
    def render_template(
        self, 
        template_name: str, 
        variables: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        """
        渲染邮件模板
        
        Args:
            template_name: 模板名称，如 'custom.submission_confirmation'
            variables: 模板变量字典
            
        Returns:
            tuple: (主题, 内容)，渲染失败返回 (None, None)
        """
        # 构建完整的模板键
        full_key = f"email.{template_name}"
        
        # 从缓存或配置获取模板
        template = self._template_cache.get(full_key)
        if not template:
            template = config.get(full_key, {})
        
        if not template:
            global_logger.error("Email", f"未找到邮件模板: {full_key}")
            return None, None
        
        subject = template.get('title', '')
        content = template.get('content', '')
        
        # 替换变量 {{variable_name}}
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            content = content.replace(placeholder, str(value))
        
        return subject, content
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        variables: Dict[str, Any],
        content_type: str = "plain"
    ) -> bool:
        """
        发送模板邮件
        
        Args:
            to_email: 收件人邮箱
            template_name: 模板名称
            variables: 模板变量
            content_type: 内容类型
            
        Returns:
            bool: 发送是否成功
        """
        subject, content = self.render_template(template_name, variables)
        
        if subject is None or content is None:
            return False
        
        return await self.send_email(to_email, subject, content, content_type)
    
    async def send_reviewer_invitation(
        self,
        to_email: str,
        reviewer_name: str,
        invitation_link: str,
        manuscript_title: Optional[str] = None
    ) -> bool:
        """
        发送审稿人邀请邮件
        
        Args:
            to_email: 审稿人邮箱
            reviewer_name: 审稿人姓名
            invitation_link: 邀请链接
            manuscript_title: 稿件标题（可选）
            
        Returns:
            bool: 发送是否成功
        """
        template = config.get('email.invite_reviewer', {})
        
        if not template:
            global_logger.error("Email", "未找到审稿人邀请模板")
            return False
        
        subject = template.get('title', 'Invitation to Review')
        content_template = template.get('content', 'Dear {}, please click: {}')
        
        # 格式化内容
        try:
            content = content_template.format(reviewer_name, invitation_link)
        except Exception:
            content = content_template.format(reviewer_name, invitation_link)
        
        # 如果提供了稿件标题，添加到内容中
        if manuscript_title:
            content = f"Manuscript: {manuscript_title}\n\n{content}"
        
        return await self.send_email(to_email, subject, content, content_type="plain")
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """
        获取可用的模板列表
        
        Returns:
            List[Dict]: 模板列表，包含 name, title, description
        """
        templates = []
        
        # 系统模板
        system_templates = [
            {"name": "verify_email", "title": "Registration Verification", "type": "system"},
            {"name": "reset_password", "title": "Password Reset", "type": "system"},
            {"name": "invite_reviewer", "title": "Reviewer Invitation", "type": "system"},
        ]
        
        # 自定义模板
        custom_templates = config.get('email.custom', {})
        for key in custom_templates.keys():
            template = custom_templates.get(key, {})
            templates.append({
                "name": f"custom.{key}",
                "title": template.get('title', key),
                "type": "custom"
            })
        
        return system_templates + templates
    
    def reload_templates(self):
        """重新加载邮件模板"""
        self._template_cache.clear()
        self._load_templates()
        global_logger.info("Email", "邮件模板已重新加载")


# 全局邮件服务实例
email_service = EmailService()
