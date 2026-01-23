from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.db.models import Task as TaskModel
from app.db.models import User as UserModel
from app.api.schemas.tasks import TaskCreate, Task as TaskSchema
from app.services.task_service import TaskService

from app.core.config import get_settings
from app.dependencies.deps import admin_required, get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskSchema)
async def create_task(
    task_in: TaskCreate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    return await TaskService.create_task(task_in, current_user, session)


@router.get("/", response_model=list[TaskSchema])
async def get_tasks(session: AsyncSession = Depends(get_db_connection)):
    return await TaskService.get_all_tasks(session)


@router.get("/my_tasks", response_model=list[TaskSchema])
async def get_user_tasks(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    return await TaskService.get_my_tasks(current_user, session)
