import random
import string
import smtplib
import tomllib

from email.mime.text import MIMEText
from core.config import config

class EmailCode:
    def __init__(self):
        self.config = config.get('global.email', {})
