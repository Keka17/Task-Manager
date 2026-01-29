from fastapi.params import Depends
from fastapi import WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_jwt_token
from app.exceptions.users import (
    UserNotFoundException,
    AdminAccessRequired,
)
from app.exceptions.tokens import InvalidTokenTypeException, InvalidTokenException
from app.db.models import User as UserModel
from app.db.database import get_db_connection


async def get_user_from_payload(payload: dict, session: AsyncSession) -> UserModel:
    """
    Retrieves the profile of the user by decoding JWT token.
    """
    if payload.get("token_type") != "access":
        raise InvalidTokenTypeException(expected_type="access")

    email: str = payload.get("sub")

    if not email:
        raise InvalidTokenException()

    query = select(UserModel).where(UserModel.email == email)
    result = await session.execute(query)
    user_in_db = result.scalars().first()

    if not user_in_db:
        raise UserNotFoundException()

    return user_in_db


async def get_current_user(
    payload: dict = Depends(decode_jwt_token),
    session: AsyncSession = Depends(get_db_connection),
) -> UserModel:
    """
    Retrieves the profile of the currently authenticated user by decoding JWT token.
    For API endpoints.
    """
    return await get_user_from_payload(payload, session)


async def admin_required(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Checks if the authenticated user has the 'is_superuser' flag set to True.
    """
    if not current_user.is_superuser:
        raise AdminAccessRequired()

    return current_user


async def get_current_user_ws(websocket: WebSocket) -> UserModel:
    """
    Retrieves the profile of the currently authenticated user by decoding JWT token.
    For WebSocket (as a query parameter).
    """
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    try:
        payload = decode_jwt_token(token)
    except:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    async with get_db_connection() as session:
        try:
            user = await get_user_from_payload(payload, session)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    return user
