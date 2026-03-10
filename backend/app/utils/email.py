import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body_html: str) -> bool:
    settings = get_settings()
    if not settings.SMTP_USER:
        logger.warning(f"SMTP not configured. Email to {to}: {subject}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.APP_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


def send_otp_email(to: str, code: str) -> bool:
    html = f"""
    <div style="font-family: sans-serif; max-width: 400px; margin: auto; padding: 20px;">
        <h2 style="color: #264653;">ExpatVault Verification</h2>
        <p>Your verification code is:</p>
        <div style="font-size: 32px; font-weight: bold; color: #2A9D8F; letter-spacing: 8px; padding: 16px; background: #F5F0E8; border-radius: 8px; text-align: center;">
            {code}
        </div>
        <p style="color: #666; font-size: 14px; margin-top: 16px;">This code expires in 5 minutes. Do not share it with anyone.</p>
    </div>
    """
    return send_email(to, "Your ExpatVault Verification Code", html)
