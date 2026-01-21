import bcrypt
import datetime
import jwt
from dns.e164 import query
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

router = APIRouter(prefix="/users", tags=["Users"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db_connection)):
    """
    User registration function with storage in the database.
    """
    query = select(UserModel).where(
        or_(UserModel.email == user.email, UserModel.phone == user.phone)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.email == user.email:
            raise EmailAlreadyExistsException(email=user.email)
        if existing_user.phone == user.phone:
            raise PhoneAlreadyExistsException(phone=user.phone)

    password_bytes = bytes(user.password, "utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    new_user = UserModel(
        name=user.name,
        hashed_password=hashed.decode("utf-8"),
        position=user.position,
        email=user.email,
        phone=user.phone,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
