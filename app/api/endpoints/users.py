from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.db.models import User as UserModel
from app.api.schemas.users import UserCreate, User as UserSchema

from app.core.config import get_settings
from app.services.user_service import UserService
from app.dependencies.deps import admin_required

router = APIRouter(prefix="/users", tags=["Users"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_db_connection)):
    """
    User registration endpoint with storage in the database.
    """
    new_user = await UserService.signup(user, session)
    return new_user


@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Extracts all users from the database.
    This endpoint is allowed to users with administrative privileges (by access token) only.
    """
    return await UserService.get_users(session)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Returns a user by their id.
    This endpoint is allowed to users with administrative privileges (by access token) only.
    """
    return await UserService.get_user_by_id(user_id, session)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Deletes a user by their ID.
    This endpoint is allowed to users with administrative privileges (by access token) only.
    """
    return await UserService.delete_user_by_id(user_id, session)
