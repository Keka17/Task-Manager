import jwt
from fastapi.params import Depends
from fastapi import WebSocket, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_jwt_token
from app.exceptions.users import (
    UserNotFoundException,
    AdminAccessRequired,
    UnauthorizedException,
)
from app.exceptions.tokens import InvalidTokenTypeException
from app.db.models import User as UserModel
from app.db.database import get_db_connection


async def get_token_cookie(request: Request):
    token = request.cookies.get("user_access_token")

    if not token:
        raise UnauthorizedException()

    return token


async def get_current_user_cookie(
    session: AsyncSession = Depends(get_db_connection),
    token: str = Depends(get_token_cookie),
) -> UserModel:
    payload = decode_jwt_token(token)

    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    email: str = payload.get("sub")

    query = select(UserModel).where(UserModel.email == email)
    result = await session.execute(query)
    user_in_db = result.scalars().first()

    if not user_in_db:
        raise UserNotFoundException()

    return user_in_db


async def admin_required(
    current_user: UserModel = Depends(get_current_user_cookie),
) -> UserModel:
    """
    Checks if the authenticated user has the 'is_superuser' flag set to True.
    """
    if not current_user.is_superuser:
        raise AdminAccessRequired()

    return current_user


async def get_current_user_ws(websocket: WebSocket) -> dict:
    """
    Retrieves the profile of the currently authenticated user by decoding JWT token.
    For WebSocket (as a query parameter).

    https://hexshift.medium.com/authenticating-websocket-clients-in-fastapi-with-jwt-and-dependency-injection-d636d48fdf48
    """
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        raise ValueError("Missing token")

    try:
        payload = decode_jwt_token(token=token)
        return payload
    except jwt.ExpiredSignatureError:
        await websocket.close(code=4001)
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        await websocket.close(code=4002)
        raise ValueError("Invalid token")
