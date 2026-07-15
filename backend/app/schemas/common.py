from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None
    errors: Optional[list[str]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[str] = Field(default_factory=list)
