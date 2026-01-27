from zoneinfo import ZoneInfo
from celery import Celery
from celery.schedules import crontab
from .revoked_token_task import cleanup_expired_tokens
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
LAST_WORK_HOUR = settings.LAST_HOUR

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.conf.timezone = LOCAL_TZ

celery_app.conf.beat_schedule = {
    "cleanup-tokens-every-day": {
        "task": cleanup_expired_tokens.name,
        "schedule": crontab(hour=0, minute=0),  # Launch every midnight (UTC)
    },
    "send_uncompleted_notification": {
        "task": send_uncompleted_task_notification.name,
        "schedule": crontab(hour="*/2", minute=0),  # Launch every 2 hours
    },
    "send_delayed_notification": {
        "task": send_delayed_task_notification.name,
        "schedule": crontab(hour=LAST_WORK_HOUR, minute=0),
    },
}

# Launch in two terminals
# celery -A app.tasks.celery_app.celery_app worker --loglevel=info
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info

# Cleaning up old tasks
# celery -A app.tasks.celery_app.celery_app purge
