from typing import Optional, Dict, Any
from modules.utils.model import SuccessResponse
from pydantic import BaseModel, Field

class AuthRegisterRequest(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    email: Optional[str] = Field(None, example="john_doe@example.com")
    password: str = Field(..., example="strong_password_123")

class AuthLoginRequest(BaseModel):
    email: str = Field(..., example="john_doe@example.com")
    password: str = Field(..., example="strong_password_123")

class AuthUser(BaseModel):
    user_name: str
    user_surname: str
    user_email: str

class AuthResponse(SuccessResponse[AuthUser]):
    data: AuthUser