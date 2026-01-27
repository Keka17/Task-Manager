from asgiref.sync import async_to_sync
from celery import shared_task
from sqlalchemy import select
from zoneinfo import ZoneInfo
from datetime import datetime
from app.db.database import AsyncSessionLocal
from app.db.models import Task

from app.core.config import get_settings
from app.utils.send_email import send_async_email
from pathlib import Path

settings = get_settings()

TEMPLATE_FOLDER = Path(__file__).parent.parent / "templates"

LOCAL_TZ = ZoneInfo(settings.TZ_IANA)


async def uncompleted_task_email():
    """
    Sends a reminder about a level A task. Works for tasks before the deadline.
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
    Sends a one-time message about an overdued level A task.
    """
    session = AsyncSessionLocal()
    now_local = datetime.now(LOCAL_TZ)
    try:
        query = (
            select(Task)
            .where(Task.importance_level == "A")
            .where(Task.completed_at.is_(None))
            .where(Task.deadline_date < now_local)
            .where(Task.overdue_notified.is_(False))
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            await send_async_email(task, "delay_notification.html")
            task.overdue_notified = True

        await session.commit()

    except Exception as e:
        await session.rollback()
        print(f"Error during sending: {e}")
    finally:
        await session.close()


@shared_task(ignore_results=True)
def send_uncompleted_task_notification():
    try:
        async_to_sync(uncompleted_task_email)()
    except Exception as e:
        print(f"Error in send_uncompleted_task_notification: {e}")


@shared_task(ignore_results=True)
def send_delayed_task_notification():
    try:
        async_to_sync(delayed_task_email)()
    except Exception as e:
        print(f"Error in send_delayed_task_notification: {e}")
