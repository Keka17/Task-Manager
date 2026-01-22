from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.api.schemas.users import UserLogin

from app.core.config import get_settings
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


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
