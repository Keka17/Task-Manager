import asyncio
import datetime
from datetime import timedelta

from celery import shared_task
from sqlalchemy import delete
from app.db.database import AsyncSessionLocal
from app.db.models import User


async def async_sql_request():
    async with AsyncSessionLocal() as session:
        try:
            # Time threshold for email verification
            cutoff = datetime.datetime.now(datetime.UTC) - timedelta(minutes=10)
            query = delete(User).where(
                User.is_verified == False, User.signed_up_at <= cutoff
            )
            await session.execute(query)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"An error occured: {e}")


@shared_task(ignore_results=True)
def delete_user_task():
    # Run the asynchronous logic within the synchronous Celery task
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_sql_request())
