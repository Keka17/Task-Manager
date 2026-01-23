from sqlalchemy.ext.asyncio import AsyncSession

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
