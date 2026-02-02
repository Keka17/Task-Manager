from sqlalchemy import select

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

    user_payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    response = await client.post("/auth/login", json=user_payload)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

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
    assert new_task.user_email == user_payload["email"]


async def test_create_task_fail(client, async_session):
    """
    Failed task creation: validation errors.
    Endpoint POST /tasks.
    """
    await add_users(async_session)

    user_payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    response = await client.post("/auth/login", json=user_payload)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

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


async def test_get_tasks_success(client, async_session):
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

    params = {"completed": False}

    response = await client.get("/tasks/", headers=headers, params=params)
    assert response.status_code == 200
    assert len(response.json()) == 1

    params = {"level": "B"}

    response = await client.get("/tasks/", headers=headers, params=params)
    assert response.status_code == 200
    assert len(response.json()) == 0
