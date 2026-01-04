import random
import string
import smtplib
import tomllib

from email.mime.text import MIMEText
from core.config import config

class EmailCode:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_inited'):
            self.config = config.get('global.email', {})
            if not self.config:
                raise ValueError("Email配置未找到")
            self._inited = True
