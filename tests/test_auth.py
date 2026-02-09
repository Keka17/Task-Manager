from freezegun import freeze_time
from sqlalchemy import select

from app.db.models import RevokedToken
from tests.utils import add_users
from tests.conftest import client, async_session

import jwt
from app.core.security import SECRET_KEY, ALGORITHM


async def test_login_success(client, async_session):
    """
    Successful login with token pair generation.
    Endpoint POST /auth/login.
    """
    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["sub"] == payload["email"]

    decoded_payload = jwt.decode(
        data["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )

    assert decoded_payload["sub"] == payload["email"]
    assert "exp" in decoded_payload


async def test_login_fail(client, async_session):
    """
    Failed login requests: user not found, invalid credentials.
    Endpoint POST /auth/login.
    """
    payload = {"email": "benedictbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"

    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$"}
    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 403
    assert response.json()["error_code"] == "INVALID_CREDENTIALS"


async def test_refresh_token_success(client, async_session):
    """
    Successful tokens update. Checks whether the old refresh token
    has been added to the db, and the ability to refresh tokens using it.
    Endpoint POST /auth/refresh.
    """
    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    with freeze_time("2026-02-01 21:20:00"):
        login_response = await client.post("/auth/login", json=payload)
        old_tokens = login_response.json()

        old_refresh_token = old_tokens["refresh_token"]
        old_payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        old_jti = old_payload["jti"]  # Old data to compare

    with freeze_time("2026-02-01 21:20:05"):
        headers = {"x-refresh-token": old_refresh_token}
        refresh_response = await client.post("/auth/refresh", headers=headers)

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()

        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

        assert new_tokens["access_token"] != old_tokens["access_token"]
        assert new_tokens["refresh_token"] != old_tokens["refresh_token"]

        # Is revoked token added to the database?
        query = select(RevokedToken).where(RevokedToken.jti == old_jti)
        result = await async_session.execute(query)
        revoked_token = result.scalars().first()

        assert revoked_token is not None

        # Attempt to refresh with the revoked token
        retry = await client.post("/auth/refresh", headers=headers)
        assert retry.status_code == 401
        assert retry.json()["error_code"] == "TOKEN_REVOKED"


async def test_refresh_token_fail(client, async_session):
    """
    Failed refresh token requests (Error 401): invalid token type, invalid token.
    Endpoint POST /auth/refresh.
    """
    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    login_response = await client.post("/auth/login", json=payload)
    access_token = login_response.json()["access_token"]
    refresh_token_garbage = login_response.json()["refresh_token"] + "garbage"

    headers = {"x-refresh-token": refresh_token_garbage}
    response_garbage = await client.post("/auth/refresh", headers=headers)

    assert response_garbage.status_code == 401
    assert response_garbage.json()["error_code"] == "INVALID_TOKEN"

    headers = {"x-refresh-token": access_token}
    response = await client.post("/auth/refresh", headers=headers)

    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_TOKEN_TYPE"

    response = await client.post("/auth/refresh")

    assert response.status_code == 400
    assert "Field: ('header', 'x-refresh-token')" in response.text


async def test_logout_success(client, async_session):
    """
    Successful logout with the revoked token added to the db.
    Endpoint POST /auth/logout.
    """
    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    login_response = await client.post("/auth/login", json=payload)
    refresh_token = login_response.json()["refresh_token"]

    headers = {"x-refresh-token": refresh_token}
    logout_response = await client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Выход из системы выполнен успешно."

    # Is revoked token added to the database?
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    expire_timestamp = payload["exp"]  # Unix format

    jti = payload["jti"]

    query = select(RevokedToken).where(RevokedToken.jti == jti)
    result = await async_session.execute(query)
    revoked_token = result.scalars().first()

    expires_at_unix = revoked_token.expires_at.timestamp()

    assert revoked_token is not None
    assert expires_at_unix == expire_timestamp


async def test_logout_fail(client, async_session):
    """
    Error 401: attempt to log out with an invalid token.
    Endpoint POST /auth/logout.
    """
    payload = {"email": "benbridgerton@example.com", "password": "Str0ngP@$$123"}
    await add_users(async_session)

    login_response = await client.post("/auth/login", json=payload)
    access_token = login_response.json()["access_token"]
    refresh_token_garbage = login_response.json()["refresh_token"] + "garbage"

    headers = {"x-refresh-token": refresh_token_garbage}
    logout_response = await client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 401
    assert logout_response.json()["error_code"] == "INVALID_TOKEN"

    headers = {"x-refresh-token": access_token}
    logout_response = await client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 401
    assert logout_response.json()["error_code"] == "INVALID_TOKEN"

    logout_response = await client.post("/auth/logout")

    assert logout_response.status_code == 400
    assert "Field: ('header', 'x-refresh-token')" in logout_response.text
