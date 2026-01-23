from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Task as TaskModel
from app.db.models import User as UserModel
from app.api.schemas.tasks import TaskCreate


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
    async def get_my_tasks(current_user: UserModel, session: AsyncSession):
        query = select(TaskModel).where(TaskModel.user_id == current_user.id)
        result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def get_all_tasks(session: AsyncSession):
        query = select(TaskModel)
        result = await session.execute(query)

        return result.scalars().all()
