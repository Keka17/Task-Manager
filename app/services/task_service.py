from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Task as TaskModel
from app.db.models import User as UserModel
from app.api.schemas.tasks import TaskCreate
from app.exceptions.tasks import TaskNotFoundException, NotAuthorException


class TaskService:
    @staticmethod
    async def create_task(
        task_data: TaskCreate,
        current_user: UserModel,
        session: AsyncSession,
    ) -> TaskModel:
        new_task = TaskModel(**task_data.model_dump(), user_id=current_user.id)

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return new_task

    @staticmethod
    async def get_all_tasks(current_user: UserModel, session: AsyncSession):
        query = select(TaskModel)
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

    @staticmethod
    async def levels_list(level: str, session: AsyncSession):
        query = select(TaskModel).where(TaskModel.importance_level == level)
        result = await session.execute(query)

        return result.scalars().all()
