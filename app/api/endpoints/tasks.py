from typing import Optional

from fastapi import APIRouter, Depends, Query, BackgroundTasks, Header
from fastapi_babel import _
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
from app.dependencies.deps import admin_required, get_current_user_cookie
from app.core.websocket_manager import manager


router = APIRouter(prefix="/tasks")


@router.post(
    "/",
    response_model=TaskSchema,
    summary="Creating a new task",
    description="**Creates a task and stored it in the database**.  \n\n"
    "- **Security**: a valid **Access Token** is required in cookies 🍪.  \n\n"
    "- **Background Tasks**: sending an email after **A**-level task creation.  \n"
    "- **Real-time**: sends a *'task_created'* notification via WebSocket.",
    tags=["Tasks"],
)
async def create_task(
    task_in: TaskCreate,
    backgroud_tasks: BackgroundTasks,
    accept_language: Optional[str] = Header(None),
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Creating a task with storage in the database.
    Only available with a valid Access Token in cookies.
    """
    new_task = await TaskService.create_task(
        task_in, accept_language, current_user, session, backgroud_tasks
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


@router.get(
    "/",
    response_model=list[TaskSchema],
    summary="List of all tasks with filtration",
    description="Retrieves all tasks from the database. A valid **Access Token** is required in cookies 🍪.  \n\n"
    "Available filters (Qery params):  \n\n"
    "- **level**: Importance level (*A, B, C, D*);  \n\n"
    "- **completed**: Completion status (*True/False*).",
    tags=["Tasks"],
)
async def get_tasks(
    level: Optional[str] = Query(default=None, min_length=1, max_length=1),
    completed: Optional[bool] = Query(default=None),
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a list of all tasks.
    Query parameters: level, completed.
    Only available with a valid Access Token in cookies.
    """
    return await TaskService.get_all_tasks(level, completed, current_user, session)


@router.get(
    "/board",
    summary="Tasks for the board",
    description="Retrieves all **uncompleted** tasks.   \n"
    "Used by the frontend to display the general kanban/board.",
    tags=["Frontend"],
)
async def get_tasks_for_board(session: AsyncSession = Depends(get_db_connection)):
    """
    Retrieving a list of all uncompleted tasks for the board.
    Used by the frontend after login.
    """
    return await TaskService.get_all_tasks_for_board(session)


@router.get(
    "/board/{task_id}",
    summary="Task details on the board",
    description="Displaying detailed information about "
    "a specific task for display in the board's modal window.",
    tags=["Frontend"],
)
async def get_task_details(
    task_id: int, session: AsyncSession = Depends(get_db_connection)
):
    """
    Retrieving a specific task by its id for the board.
    Used by the frontend after login.
    """
    return await TaskService.get_task_by_id_board(task_id, session)


@router.get(
    "/my_tasks",
    response_model=list[TaskSchema],
    summary="My tasks",
    description="Retrieves a list of all tasks created by the **current authorized user**.",
    tags=["Tasks"],
)
async def get_user_tasks(
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a list of all user tasks.
    Only available with a valid Access Token in cookies.
    """
    return await TaskService.get_my_tasks(current_user, session)


@router.get(
    "/{task_id}",
    response_model=TaskSchema,
    summary="Retrieve a specific tasks by ID",
    description="Retrieves detailed information about the task.  \n\n"
    "**Security**: a valid **Access Token** is required in cookies 🍪.",
    responses={
        404: {"description": "Task not found"},
    },
    tags=["Tasks"],
)
async def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Retrieving a specific task by its id.
    Only available with a valid Access Token in the Authorization header.
    """
    return await TaskService.get_task_by_id(task_id, current_user, session)


@router.patch(
    "/{task_id}",
    response_model=TaskSchema,
    summary="Editing task content",
    description="Updates the 'content' text field of the task.  \n\n"
    "- **Restriction**: Only the author of the task can edit it.  \n\n"
    "- **Real-time**: sends a *'task_updated'* notification via WebSocket.",
    tags=["Tasks"],
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Updating the "content" field of a specific task by.
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


@router.patch(
    "/complete/{task_id}",
    summary="Completion of the task",
    description="Adds a timestamp in the '*completed_at*' field."
    "Only available to the **author**.  \n\n"
    "**Real-time**: sends a *'task_completed'* notification via WebSocket.",
    tags=["Tasks"],
)
async def complete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Adding a timestamp to the 'completed_at' field as a task
    completion indicator. Only available to its author.
    """
    task_to_complete = await TaskService.complete_task(task_id, current_user, session)
    await manager.broadcast({"event": "task_completed", "task": task_to_complete.title})
    return {
        "message": _("Задача '%(title)s' завершена.")
        % {"title": task_to_complete.title}
    }


@router.patch(
    "/remark/{task_id}",
    response_model=TaskSchema,
    summary="Adding a comment (Admin)",
    description="Allows the administrator to add a remark on the task.  \n\n"
    "**Background Tasks**: sending an email after creating a remark.",
    tags=["Tasks"],
)
async def create_remark(
    task_id: int,
    task_update: TaskUpdateAdmin,
    backgroud_tasks: BackgroundTasks,
    accept_language: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Creating a remark for a specific task.
    Only available to users with administrative privileges.
    """
    return await TaskService.create_remark(
        task_id, task_update, accept_language, session, backgroud_tasks
    )


@router.delete(
    "/{task_id}",
    summary="Deleting a task",
    description="Permanently delete a task from the database.  \n\n"
    "**Restriction**: Only the author OR admin can delete a task. \n\n"
    "**Real-time**: sends a *'task_deleted'* notification via WebSocket.",
    tags=["Tasks"],
)
async def delete_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Deleting a specific task. Only available to its author and to users with administrative privileges.
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
    return {"message": _("Задача '%(title)s' успешно удалена.") % {"title": task_title}}
