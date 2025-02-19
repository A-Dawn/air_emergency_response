# utils/email.py
from flask_mail import Mail, Message
from flask import current_app

def send_email(to, subject, body):
    """
    发送邮件
    :param to: 收件人邮箱地址
    :param subject: 邮件主题
    :param body: 邮件正文 (可以是 HTML)
    """
    mail = Mail(current_app)
    msg = Message(subject, recipients=[to], html=body)
    try:
        mail.send(msg)
        return True  # 发送成功
    except Exception as e:
        print(f"邮件发送失败: {e}")  # 记录错误日志
        return False  # 发送失败
