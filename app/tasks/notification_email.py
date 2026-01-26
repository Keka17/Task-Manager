import asyncio
from celery import shared_task
from sqlalchemy import select
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from zoneinfo import ZoneInfo
from datetime import datetime
from app.db.database import AsyncSessionLocal
from app.db.models import Task

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


async def uncompleted_task_email():
    """
    Asynchronous function to send notification about A-level task.
    """
    session = AsyncSessionLocal()
    now_local = datetime.now(LOCAL_TZ)
    try:
        query = (
            select(Task)
            .where(Task.importance_level == "A")
            .where(Task.completed_at.is_(None))
            .where(Task.deadline_date > now_local)
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            await send_async_email(task, "task_notification.html")
    except Exception as e:
        await session.rollback()
        print(f"Error during sending: {e}")
    finally:
        await session.close()


async def delayed_task_email():
    """
    Asynchronous function to send notification about overdue A-level task.
    """
    session = AsyncSessionLocal()
    now_local = datetime.now(LOCAL_TZ)
    try:
        query = (
            select(Task)
            .where(Task.importance_level == "A")
            .where(Task.completed_at.is_(None))
            .where(Task.deadline_date < now_local)
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            await send_async_email(task, "delay_notification.html")
    except Exception as e:
        await session.rollback()
        print(f"Error during sending: {e}")
    finally:
        await session.close()


@shared_task(ignore_results=True)
def send_uncompleted_task_notification():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(uncompleted_task_email())


@shared_task(ignore_results=True)
def send_delayed_task_notification():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(delayed_task_email())
