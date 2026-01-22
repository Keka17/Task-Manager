import bcrypt
import datetime
import jwt
from jwt import PyJWTError
from fastapi import APIRouter, Depends, Header

from app.db.database import get_db_connection
from app.api.schemas.users import UserCreate, UserLogin, User as UserSchema
from app.db.models import RevokedToken, User as UserModel
from app.exceptions.users import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    PhoneAlreadyExistsException,
    InvalidCredentialsException,
    AdminAccessRequired,
)
from app.exceptions.tokens import (
    InvalidTokenException,
    InvalidTokenTypeException,
    TokenRevokedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
)

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_db_connection)):
    new_user = await UserService.signup(user, session)
    return new_user


@router.post("/login")
async def login(user_in: UserLogin, session: AsyncSession = Depends(get_db_connection)):
    tokens = await AuthService.login(user_in, session)
    return tokens


@router.post("/refresh")
async def refresh_token(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    new_tokens = await AuthService.refresh(x_refresh_token, session)
    return new_tokens


@router.post("/logout")
async def logout(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    result = await AuthService.logout(x_refresh_token, session)
    return result
