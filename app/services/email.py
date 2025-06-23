from aiosmtplib import SMTP
from email.message import EmailMessage
from app.core.config import settings

async def send_verification_email(email: str, code: str) -> None:
    """
    Посылает на указанный email письмо с кодом верификации.
    """
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    msg["Subject"] = "Verify your Coffee Shop account"
    msg.set_content(f"Your verification code is: {code}")

    # подключаемся к SMTP-серверу
    smtp = SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )
    await smtp.connect()
    await smtp.send_message(msg)
    await smtp.quit()