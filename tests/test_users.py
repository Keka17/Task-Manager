from fastapi.testclient import TestClient
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


async def test_create_user_success(client, async_session):
    """
    Successful user creation test.
    Endpoint POST /users/signup.
    """
    payload = {
        "name": "Брэдшоу Кэролайн Сергеевна",
        "position": "CEO",
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


async def test_create_user_duplicate(client, async_session):
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

    assert response.status_code == 409
    assert response.json()["error_code"] == "CONFLICT"
