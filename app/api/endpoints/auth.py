from fastapi import APIRouter, Depends, Header, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from app.db.database import get_db_connection
from app.api.schemas.users import UserLogin

from app.core.config import get_settings
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
templates = Jinja2Templates(directory="app/templates")


@router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Displays the HTML login page for the board.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(user_in: UserLogin, session: AsyncSession = Depends(get_db_connection)):
    """
    Verifying credentials to get a JWT token.
    """
    tokens = await AuthService.login(user_in, session)
    return tokens


@router.post("/refresh")
async def refresh_token(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Updates a pair of tokens.
    Accepts the old Refresh Token in Headers, revokes it (add to the database)
    and generates new Access and Refresh tokens.
    """
    new_tokens = await AuthService.refresh(x_refresh_token, session)
    return new_tokens


@router.post("/logout")
async def logout(
    x_refresh_token: str = Header(...),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Ends the user session. Accepts Refresh Token in Headers,
    retrieves the JTI from the current token and adds it to the database.
    """
    result = await AuthService.logout(x_refresh_token, session)
    return result
