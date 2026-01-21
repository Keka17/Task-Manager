from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.routers import users
from app.exceptions.base import AppException

from app.handlers.exceptions import app_exception_handler
from app.handlers.validation_errors import validation_exception_handler
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG", colorize=True)

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "API is running!"}
