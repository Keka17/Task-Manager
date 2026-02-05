from sqlalchemy import select
from app.db.models import User
from tests.utils import add_users

from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from tests.conftest import mock_settings, client, async_session


async def test_create_user_success(client, async_session):
    """
    Successful user creation test.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Брэдшоу Кэролайн Сергеевна",
        "position": "SMM-специалист",
        "email": "carrie_ny@example.com",
        "phone": "89649264354",
        "password": "Il0veM@ano1o",
    }

    response = await client.post("/users/signup", json=payload)

    assert response.status_code == 200

    query = select(User).where(User.email == payload["email"])
    result = await async_session.execute(query)
    new_user = result.scalars().first()

    assert new_user.id is not None
    assert new_user.is_superuser is False
    assert new_user.name == payload["name"]
    assert new_user.hashed_password != payload["password"]


async def test_create_user_duplicate(client, async_session, mock_settings):
    """
    Error 409: creating a user that already exists.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Бриджертон Бенедикт Эдмундович",
        "position": "UI-дизайнер",
        "email": "benbridgerton@example.com",
        "phone": "89159987867",
        "password": "Str0ngP@$$123",
    }
    await add_users(async_session)

    response = await client.post("/users/signup", json=payload)
    print(response.json())
    assert response.status_code == 409
    assert response.json()["error_code"] == "CONFLICT"


async def test_create_user_fail(client, async_session, mock_settings):
    """
    Validation Errors: invalid domain, phone number, position and weak password.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Брэдшоу Кэролайн Сергеевна",
        "position": "Стажер SMM",
        "email": "carrie_ny@gmail.com",
        "phone": "+79649264354",
        "password": "passWOrd",
    }
    response = await client.post("/users/signup", json=payload)

    assert response.status_code == 400

    assert "Field: ('body', 'position')" in response.text
    assert "Позиции не существует" in response.text
    assert "Field: ('body', 'email')" in response.text
    assert "Регистрация доступна только для сотрудников" in response.text
    assert "Field: ('body', 'phone')" in response.text
    assert "Некорректная запись!" in response.text
    assert "Field: ('body', 'password')" in response.text
    assert "Слабый пароль!" in response.text


async def test_get_users_access_control(client, async_session):
    """
    Testing endpoint access control (admin only).
    Endpoint GET /users.
    """
    await add_users(async_session)

    admin_token = create_access_token({"sub": "dundermifflin@example.com"})
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    response_admin = await client.get("/users/", headers=headers_admin)

    assert response_admin.status_code == 200
    assert len(response_admin.json()) == 3

    # Authorization with invalid token type (refresh)
    admin_refresh_token = create_refresh_token({"sub": "dundermifflin@example.com"})
    headers = {"Authorization": f"Bearer {admin_refresh_token}"}

    response = await client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"

    # Regular user without administrative privileges
    user_token = create_access_token({"sub": "p.parker@example.com"})
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = await client.get("/users/", headers=headers_user)
    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"

    # Trying to reach without auth
    response = await client.get("/users/")
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


async def test_get_user_access_control(client, async_session):
    """
    Testing endpoint access control (admin only).
    Endpoint GET /users/{user_id}.
    """
    await add_users(async_session)

    admin_token = create_access_token({"sub": "dundermifflin@example.com"})
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    existing_user_id = 2

    response_admin = await client.get(
        f"/users/{existing_user_id}", headers=headers_admin
    )
    assert response_admin.status_code == 200

    user = response_admin.json()
    assert user["name"] == "Паркер Питер Бенджами"

    non_existing_user_id = 999

    response_admin = await client.get(
        f"/users/{non_existing_user_id}", headers=headers_admin
    )
    assert response_admin.status_code == 404
    assert response_admin.json()["error_code"] == "NOT_FOUND"

    # Regular user without administrative privileges
    user_token = create_access_token({"sub": "p.parker@example.com"})
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = await client.get(f"/users/{existing_user_id}", headers=headers_user)
    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"

    # Trying to reach without auth
    response = await client.get(f"/users/{existing_user_id}")
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"


async def test_delete_user_access_control(client, async_session):
    """
    Testing endpoint access control (admin only).
    Endpoint DELETE /users/{user_id}.
    """
    await add_users(async_session)
    admin_token = create_access_token({"sub": "dundermifflin@example.com"})
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    existing_user_id = 3

    response_admin = await client.delete(
        f"/users/{existing_user_id}", headers=headers_admin
    )

    assert response_admin.status_code == 200
    assert "успешно удален" in response_admin.json()["message"]

    # Check the db
    query = select(User).where(User.id == existing_user_id)
    result = await async_session.execute(query)
    deleted_user = result.scalars().first()

    assert deleted_user is None

    non_existing_user_id = 999

    response_admin = await client.delete(
        f"/users/{non_existing_user_id}", headers=headers_admin
    )

    assert response_admin.status_code == 404
    assert response_admin.json()["error_code"] == "NOT_FOUND"

    # Regular user without administrative privileges
    user_token = create_access_token({"sub": "p.parker@example.com"})
    headers_user = {"Authorization": f"Bearer {user_token}"}

    response_user = await client.delete(
        f"/users/{existing_user_id}", headers=headers_user
    )
    assert response_user.status_code == 403
    assert response_user.json()["error_code"] == "FORBIDDEN"

    # Trying to reach without auth
    response = await client.delete(f"/users/{existing_user_id}")
    assert response.status_code == 401
    assert response.json()["error_code"] == "UNAUTHORIZED"
