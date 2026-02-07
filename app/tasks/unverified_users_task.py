import asyncio
from celery import shared_task
from sqlalchemy import delete

from app.db.database import AsyncSessionLocal
from app.db.models import User


async def sql_request():
    """
    Asynchronous function to perform sql-delete operation.
    """
    async with AsyncSessionLocal() as session:
        try:
            query = delete(User).where(User.is_verified == False)
            await session.execute(query)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error during cleanup: {e}")


@shared_task(ignore_result=True)
def cleanup_unverified_users():
    """
    Periodic task to remove unverified users from the database.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sql_request())
