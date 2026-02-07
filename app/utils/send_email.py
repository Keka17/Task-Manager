from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from pathlib import Path
from loguru import logger

settings = get_settings()

TEMPLATE_FOLDER = Path(__file__).parent.parent / "templates"

LOCAL_TZ = ZoneInfo(settings.TZ_IANA)


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,  # Use True for Port 587
    MAIL_SSL_TLS=True,  # Use True for Port 465
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)


async def send_async_email(task, subject, template):
    """
    Asynchronous sending of notification letters about A-level tasks / admin remark.
    """
    deadline = task.deadline_date.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")
    template_data = {
        "title": task.title,
        "content": task.content,
        "deadline": deadline,
        "admin_email": settings.ADMIN_EMAIL,
        "remark": task.remark,
    }

    message = MessageSchema(
        subject=subject,
        recipients=[task.user_email],
        template_body=template_data,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name=template)
    except Exception as e:
        message = f"Error during sending a mail to {task.user_email}:\n{e}"
        logger.add(lambda m: print(message, end=""), level="ERROR")


async def send_confirmation_email(to_email, link, subject, template):
    template_data = {"link": link}

    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        template_body=template_data,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name=template)
    except Exception as e:
        message = f"Error during sending a mail to {to_email}:\n{e}"
        logger.add(lambda m: print(message, end=""), level="ERROR")
