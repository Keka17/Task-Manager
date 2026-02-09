from zoneinfo import ZoneInfo
from celery import Celery
from celery.schedules import crontab
from .revoked_token_task import cleanup_expired_tokens
from .unverified_user_task import delete_user_task
from .notification_email import (
    send_uncompleted_task_notification,
    send_delayed_task_notification,
)
from app.core.config import get_settings

settings = get_settings()

"""
Celery settings for asynchronous task processing and scheduled tasks.

Redis is used as:
- a message broker for task distribution between the application and workers;
- a backendfor storing results, which keeps track of task execution status.
"""
LOCAL_TZ = ZoneInfo(settings.TZ_IANA)

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.conf.timezone = LOCAL_TZ

celery_app.conf.beat_schedule = {
    "cleanup_tokens_every_day": {
        "task": cleanup_expired_tokens.name,
        "schedule": crontab(hour=0, minute=0),  # Launch every midnight (UTC)
    },
    "delete_unverified_users": {
        "task": delete_user_task.name,
        "schedule": crontab(minute="*/5"),
    },
    "send_uncompleted_notification": {
        "task": send_uncompleted_task_notification.name,
        "schedule": crontab(hour="*/2", minute=0),  # Launch every 2 hours
    },
    "send_delayed_notification": {
        "task": send_delayed_task_notification.name,
        "schedule": crontab(minute="*/30"),
    },
}

# Launch in two terminals
# celery -A app.tasks.celery_app.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info

# Cleaning up old tasks
# celery -A app.tasks.celery_app.celery_app purge
