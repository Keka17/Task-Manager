from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status_code: int
    message: str
    error_code: str
