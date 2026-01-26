from typing import Optional

from fastapi import APIRouter, Depends, Query
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
    """
    Creating a task with storage in the database.
    Only accessible with a valid Access Token in the Authorization header.
    """
    return await TaskService.create_task(task_in, current_user, session)


@router.get("/", response_model=list[TaskSchema])
async def get_tasks(
    level: Optional[str] = Query(default=None, min_length=1, max_length=1),
    completed: Optional[bool] = Query(default=None),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a list of all tasks.
    Query parameters: level (importance_level), completed (if completed_at is not Null).
    Only accessible with a valid Access Token in the Authorization header.
    """
    return await TaskService.get_all_tasks(level, completed, current_user, session)


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a specific task by its id.
    Only accessible with a valid Access Token in the Authorization header.
    """
    return await TaskService.get_task_by_id(task_id, current_user, session)


@router.get("/my", response_model=list[TaskSchema])
async def get_user_tasks(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a list of all user tasks.
    Only accessible with a valid Access Token in the Authorization header.
    """
    return await TaskService.get_my_tasks(current_user, session)


@router.patch("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Updating the "content" field of a specific task.
    Only available to its author.
    """
    return await TaskService.update_task(task_id, task_update, current_user, session)


@router.patch("/complete/{task_id}", response_model=TaskSchema)
async def complete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Adds a timestamp to the 'completed_at' field as a task
    completion indicator. Only available to its author.
    """
    return await TaskService.complete_task(task_id, current_user, session)


@router.patch("/remark/{task_id}", response_model=TaskSchema)
async def create_remark(
    task_id: int,
    task_update: TaskUpdateAdmin,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Creating a remark for a specific task.
    Only available to users with administrative privileges only.
    """
    return await TaskService.create_remark(task_id, task_update, session)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Deleting a specific task. Only available to its author.
    """
    return await TaskService.delete_task(task_id, current_user, session)
