from typing import Optional

from fastapi import APIRouter, Depends, Query, BackgroundTasks
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
from app.core.websocket_manager import manager

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskSchema)
async def create_task(
    task_in: TaskCreate,
    backgroud_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Creating a task with storage in the database.
    Only accessible with a valid Access Token in the Authorization header.
    """
    new_task = await TaskService.create_task(
        task_in, current_user, session, backgroud_tasks
    )
    await manager.broadcast(
        {
            "event": "task_created",
            "name": current_user.name,
            "task_id": new_task.id,
            "level": new_task.importance_level,
            "title": new_task.title,
        }
    )

    return new_task


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


@router.get("/board")
async def get_tasks_for_board(session: AsyncSession = Depends(get_db_connection)):
    """
    Retrieving a list of all uncompleted tasks for the board.
    Used by tge frontend after login.
    """
    return await TaskService.get_all_tasks_for_board(session)


@router.get("/board/{task_id}")
async def get_task_details(
    task_id: int, session: AsyncSession = Depends(get_db_connection)
):
    """
    Retrieving a specific task by its id for the board.
    Used by tge frontend after login.
    """
    return await TaskService.get_task_by_id_board(task_id, session)


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
    updated_task = await TaskService.update_task(
        task_id, task_update, current_user, session
    )
    await manager.broadcast(
        {
            "event": "task_updated",
            "task_id": updated_task.id,
            "level": updated_task.importance_level,
            "title": updated_task.title,
            "content_upd": updated_task.content,
        }
    )

    return updated_task


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
    task_to_complete = await TaskService.complete_task(task_id, current_user, session)
    await manager.broadcast({"event": "task_completed", "task": task_to_complete.title})
    return {"message": f"Задача '{task_to_complete.title}' завершена."}


@router.patch("/remark/{task_id}", response_model=TaskSchema)
async def create_remark(
    task_id: int,
    task_update: TaskUpdateAdmin,
    backgroud_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Creating a remark for a specific task.
    Only available to users with administrative privileges only.
    """
    return await TaskService.create_remark(
        task_id, task_update, session, backgroud_tasks
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Deleting a specific task. Only available to its author.
    """
    task_to_delete = await TaskService.get_task_by_id(task_id, current_user, session)
    task_title = task_to_delete.title
    await TaskService.delete_task(task_id, current_user, session)
    await manager.broadcast(
        {
            "event": "task_deleted",
            "title": task_title,
        }
    )
    return {"message": f"Задача '{task_title}' успешно удалена."}
