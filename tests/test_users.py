from sqlalchemy import select
from app.db.models import User
from tests.utils import add_users

import jwt
from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    create_refresh_token,
)
from tests.conftest import mock_settings


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


async def test_create_user_bad_domain_position(client, async_session, mock_settings):
    """
    Validation Error 400: non-existent position and invalid domain.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Брэдшоу Кэролайн Сергеевна",
        "position": "Стажер SMM",
        "email": "carrie_ny@gmail.com",
        "phone": "89649264354",
        "password": "Il0veM@ano1o",
    }
    response = await client.post("/users/signup", json=payload)

    assert response.status_code == 400
    assert "Field: ('body', 'email')" in response.text
    assert "Регистрация доступна только для сотрудников" in response.text
    assert "Field: ('body', 'position')" in response.text
    assert "Позиции не существует" in response.text


async def test_create_user_bad_password_phone(client, async_session):
    """
    Validation Error 400: a weak password and invalid phone number.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Брэдшоу Кэролайн Сергеевна",
        "position": "SMM-специалист",
        "email": "carrie_ny@example.com",
        "phone": "+79649264354",
        "password": "passWOrd",
    }

    response = await client.post("/users/signup", json=payload)

    assert response.status_code == 400
    assert "Field: ('body', 'phone')" in response.text
    assert "Некорректная запись!" in response.text
    assert "Field: ('body', 'password')" in response.text
    assert "Слабый пароль!" in response.text
