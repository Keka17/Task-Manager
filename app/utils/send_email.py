from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from pathlib import Path

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


async def send_async_email(task, template):
    """
    Asynchronous sending of notification letters about level A tasks.
    """
    deadline = task.deadline_date.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")
    template_data = {
        "title": task.title,
        "content": task.content,
        "deadline": deadline,
        "admin_email": settings.ADMIN_EMAIL,
    }

    message = MessageSchema(
        subject=f"Уведомление о задаче наивысшего приоритета",
        recipients=[task.user_email],
        template_body=template_data,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name=template)
