from loguru import logger
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi_babel import BabelConfigs, BabelMiddleware

from app.api.endpoints import users, auth, tasks
from app.api import websocket_board
from app.exceptions.base import AppException
from app.core.templates import templates

from app.middlewares.logs import loguru_middleware
from app.handlers.exceptions import app_exception_handler
from app.handlers.validation_errors import validation_exception_handler

logger.remove()

# Console logs
logger.add(
    sys.stderr,
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    colorize=True,
)

# Different levels logs
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="500 MB",
    retention="10 days",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    "logs/warnings.log",
    level="WARNING",
    rotation="10 MB",
    retention="5 day",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="10 MB",
    retention="1 day",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


app = FastAPI(
    title="Task Manager API",
    description="This is a real-time task manager with an interactive board",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide models section by default
        "docExpansion": "none",  # Collapse all sections by default,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
        "persistAuthorization": True,
    },
)


babel_configs = BabelConfigs(
    ROOT_DIR=Path(__file__).parent / "locales",
    BABEL_DEFAULT_LOCALE="ru",
    BABEL_TRANSLATION_DIRECTORY="locales",
)

app.add_middleware(
    BabelMiddleware, babel_configs=babel_configs, jinja2_templates=templates
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.middleware("http")(loguru_middleware)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(websocket_board.router)


@app.get("/")
def root():
    return {"message": "API is running!"}
