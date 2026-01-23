from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.db.models import User as UserModel
from app.api.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskUpdateAdmin,
    Task as TaskSchema,
)
from app.services.task_service import TaskService
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


@router.get("/level/{level}", response_model=list[TaskSchema])
async def get_tasks_by_level(
    level: str,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    return await TaskService.levels_list(level, session)


@router.patch("/update/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    return await TaskService.update_task(task_id, task_update, current_user, session)


@router.patch("/{task_id}/remark", response_model=TaskSchema)
async def create_remark(
    task_id: int,
    task_update: TaskUpdateAdmin,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    return await TaskService.create_remark(task_id, task_update, session)


@router.delete("/delete/{task_id}")
async def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    return await TaskService.delete_task(task_id, current_user, session)
