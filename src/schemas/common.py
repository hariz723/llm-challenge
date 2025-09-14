from pydantic import BaseModel
from typing import Optional, Any


class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: int
    error_message: str
