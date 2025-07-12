import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from app.settings.config import base_config
from app.settings.log import logger


def send_email(receiver: str, subject: str, body: str):
    host = base_config.get_config("email", "host")
    port = base_config.get_config("email", "port")
    username = base_config.get_config("email", "username")
    password = base_config.get_config("email", "password")
    sender = base_config.get_config("email", "sender")
    message = MIMEMultipart()
    message["From"] = formataddr(pair=(sender, username))
    message["To"] = receiver
    message["Subject"] = Header(subject, "utf-8").encode()
    message.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(host, int(port)) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(username, password)
            smtp_server.sendmail(username, receiver, message.as_string())
        logger.sysLogger.info(f"发送邮件给{receiver}成功")
        return True
    except Exception as e:
        logger.sysLogger.error(f"发送邮件给{receiver}失败：{e}")
        return False



