from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Task as TaskModel
from app.db.models import User as UserModel
from app.api.schemas.tasks import TaskCreate
from app.exceptions.tasks import (
    TaskNotFoundException,
    NotAuthorException,
    InvalidImportanceLevelException,
    TaskAlreadyCompletedException,
)

from app.core.config import get_settings

settings = get_settings()


class TaskService:
    @staticmethod
    async def create_task(
        task_data: TaskCreate,
        current_user: UserModel,
        session: AsyncSession,
    ) -> TaskModel:
        from zoneinfo import ZoneInfo

        LOCAL_TZ = ZoneInfo(settings.TZ_IANA)
        now_local = datetime.now(LOCAL_TZ)

        level = task_data.importance_level
        deadline = None

        if level == "A":
            deadline = now_local.replace(hour=18, minute=0, second=0, microsecond=0)

            if now_local > deadline:
                deadline += timedelta(days=1)
        elif level == "B":
            deadline = now_local + timedelta(days=7)
        elif level == "C":
            deadline = now_local + timedelta(hours=24)
        else:
            deadline = now_local + timedelta(days=30)

        new_task = TaskModel(
            **task_data.model_dump(), user_id=current_user.id, deadline_date=deadline
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return new_task

    @staticmethod
    async def get_all_tasks(
        level: str, completed: bool, current_user: UserModel, session: AsyncSession
    ):
        query = select(TaskModel)

        if level:
            levels = ["A", "B", "C", "D"]
            if level not in levels:
                raise InvalidImportanceLevelException()

            query = query.where(TaskModel.importance_level == level)

        if completed is True:
            query = query.where(TaskModel.completed_at.isnot(None))
        elif completed is False:
            query = query.where(TaskModel.completed_at.is_(None))

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_my_tasks(current_user: UserModel, session: AsyncSession):
        query = select(TaskModel).where(TaskModel.user_id == current_user.id)
        result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def update_task(
        task_id: int, task_update, current_user: UserModel, session: AsyncSession
    ):
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(query)
        task_in_db = result.scalars().first()

        if not task_in_db:
            raise TaskNotFoundException(task_id)

        if task_in_db.user_email != current_user.email:
            raise NotAuthorException()

        if task_update.content:
            task_in_db.content = task_update.content

        await session.commit()
        await session.refresh(task_in_db)

        return task_in_db

    @staticmethod
    async def complete_task(
        task_id: int, current_user: UserModel, session: AsyncSession
    ):
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(query)
        task_in_db = result.scalars().first()

        if not task_in_db:
            raise TaskNotFoundException(task_id)

        if task_in_db.user_email != current_user.email:
            raise NotAuthorException()

        if task_in_db.completed_at:
            raise TaskAlreadyCompletedException()

        completion_time = datetime.now(timezone.utc)
        task_in_db.completed_at = completion_time

        await session.commit()
        await session.refresh(task_in_db)

        return task_in_db

    @staticmethod
    async def create_remark(task_id: int, task_remark, session: AsyncSession):
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(query)
        task = result.scalars().first()

        if not task:
            raise TaskNotFoundException(task_id)

        if task_remark.remark:
            task.remark = task_remark.remark

        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def delete_task(
        task_id: int, current_user: UserModel, session: AsyncSession
    ) -> dict:
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(query)
        task_in_db = result.scalars().first()

        if not task_in_db:
            raise TaskNotFoundException(task_id)

        if current_user.email != task_in_db.user_email:
            raise NotAuthorException()

        await session.delete(task_in_db)
        await session.commit()

        return {"message": f"Задача с id = {task_id} успешно удалена."}
