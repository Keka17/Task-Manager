from sqlalchemy import select
from unittest.mock import MagicMock
from fastapi import BackgroundTasks

from app.db.models import Task
from app.core.security import create_access_token
from tests.utils import add_users, add_tasks
from tests.conftest import client, async_session


async def test_create_task_success(client, async_session):
    """
    Successful task creatin test.
    Endpoint POST /tasks.
    """
    # Get a valid access token
    await add_users(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Test title",
        "content": "Test content",
        "importance_level": "B",
    }

    response = await client.post("/tasks/", headers=headers, json=payload)

    assert response.status_code == 200

    query = select(Task).where(Task.title == payload["title"])
    result = await async_session.execute(query)
    new_task = result.scalars().first()

    assert new_task is not None
    assert new_task.id is not None
    assert new_task.title == payload["title"]
    assert new_task.user_email == "benbridgerton@example.com"

    # Trying to reach without auth
    response = await client.post("/tasks/", json=payload)
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


async def test_create_task_fail(client, async_session):
    """
    Failed task creation: validation errors.
    Endpoint POST /tasks.
    """
    await add_users(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "test title",
        "content": "test content",
        "importance_level": "E",
    }

    response = await client.post("/tasks/", headers=headers, json=payload)

    assert response.status_code == 400
    assert "Field: ('body', 'title')" in response.text
    assert "Заголовок должен начинаться" in response.text
    assert "Field: ('body', 'content')" in response.text
    assert "Содержание задачи" in response.text
    assert "Field: ('body', 'importance_level')" in response.text
    assert "Некорректная запись уровня важности" in response.text


async def test_get_tasks(client, async_session):
    """
    Test for retrieving all tasks.
    Requests with query parameters.
    Endpoint GET /tasks.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/tasks/", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Background Jobs: Processing User-Generated Content"
    assert data[0]["remark"] is None
    assert data[1]["user_email"] == "benbridgerton@example.com"

    # Query params
    params = {"completed": False}

    response = await client.get("/tasks/", headers=headers, params=params)
    assert response.status_code == 200
    assert len(response.json()) == 1

    params = {"level": "B"}

    response = await client.get("/tasks/", headers=headers, params=params)

    assert response.status_code == 200
    assert len(response.json()) == 0

    params = {"completed": False, "level": "C"}

    response = await client.get("/tasks/", headers=headers, params=params)

    assert response.status_code == 200
    assert len(response.json()) == 1

    # Invalid level
    params = {"level": "E"}

    response = await client.get("/tasks/", headers=headers, params=params)

    assert response.status_code == 422
    assert response.json()["error_code"] == "UNPROCESSABLE_ENTITY"

    # No token headers
    response = await client.get("/tasks/")

    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


async def test_get_task(client, async_session):
    """
    Test for retrieving a specific task by its id.
    Endpoint GET /tasks/{task_id}.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    task_id = 53

    response = await client.get(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert (
        response.json()["title"] == "Background Jobs: Processing User-Generated Content"
    )

    non_exs_task_id = 66
    response = await client.get(f"/tasks/{non_exs_task_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


async def test_get_my_tasks(client, async_session):
    """
    Test for retrieving user's task.
    Endpoint GET /tasks/my.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/tasks/my_tasks", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_email"] == "benbridgerton@example.com"


async def test_update_tasks(client, async_session):
    """
    Task update test. Only available to its author.
    Endpoint PATCH /tasks/{task_id}.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"content": "test"}

    task_id = 40

    response = await client.patch(f"/tasks/{task_id}", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["user_email"] == "benbridgerton@example.com"
    assert "test" in response.json()["content"]

    non_exs_task_id = 66

    response = await client.patch(
        f"/tasks/{non_exs_task_id}", headers=headers, json=payload
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    # Not author
    task_id = 53

    response = await client.patch(f"/tasks/{task_id}", headers=headers, json=payload)

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"


async def test_complete_task(client, async_session):
    """
    Task completion test. Only available to its author.
    Endpoint PATCH /tasks/complete/{task_id}.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "p.parker@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    task_id = 53

    response = await client.patch(f"/tasks/complete/{task_id}", headers=headers)

    assert response.status_code == 200

    assert (
        response.json()["message"]
        == "Задача 'Background Jobs: Processing User-Generated Content' завершена."
    )

    # Already completed
    response = await client.patch(f"/tasks/complete/{task_id}", headers=headers)

    assert response.status_code == 400
    assert response.json()["error_code"] == "BAD_REQUEST"

    non_exs_task_id = 66

    response = await client.patch(f"/tasks/complete/{non_exs_task_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    # Not author
    task_id = 40

    response = await client.patch(f"/tasks/complete/{task_id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"


async def test_create_remark(client, async_session):
    """
    Test for adding a remark to a task.
    Only available to admins.
    Endpoint PATCH /tasks/remark/{task_id}.
    """
    # Mock the add_task method
    BackgroundTasks.add_task = MagicMock()

    await add_users(async_session)
    await add_tasks(async_session)

    token = create_access_token({"sub": "dundermifflin@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    task_id = 53

    payload = {"remark": "test remark"}

    response = await client.patch(
        f"/tasks/remark/{task_id}", headers=headers, json=payload
    )

    assert response.status_code == 200
    assert response.json()["remark"] == payload["remark"]
    assert response.json()["id"] == task_id

    non_exs_task_id = 66
    response = await client.patch(
        f"/tasks/remark/{non_exs_task_id}", headers=headers, json=payload
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    # Not admin
    token = create_access_token({"sub": "p.parker@example.com"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        f"/tasks/remark/{task_id}", headers=headers, json=payload
    )
    assert response.status_code == 403
    assert response.json()["message"] == "Запрещено: требуется доступ администратора."


async def test_delete_task(client, async_session):
    """
    Task delete test. Only available to its author.
    Endpoint PATCH /tasks/{task_id}.
    """
    await add_users(async_session)
    await add_tasks(async_session)

    # Admin
    token = create_access_token({"sub": "dundermifflin@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    task_id = 53

    response = await client.delete(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert "успешно удалена" in response.json()["message"]

    # Author
    token = create_access_token({"sub": "benbridgerton@example.com"})
    headers = {"Authorization": f"Bearer {token}"}
    task_id = 40

    response = await client.delete(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert "успешно удалена" in response.json()["message"]

    # Check the db
    query = select(Task).where(Task.id == task_id)
    result = await async_session.execute(query)
    deleted_task = result.scalars().first()

    assert deleted_task is None

    non_exs_task_id = 66
    response = await client.delete(f"/tasks/{non_exs_task_id}", headers=headers)

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    await add_tasks(async_session)

    # Not author
    task_id = 53

    response = await client.delete(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"
