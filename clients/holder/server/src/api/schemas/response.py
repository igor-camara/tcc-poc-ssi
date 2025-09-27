from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: int
    message: str

class AuthResponse(BaseModel):
    user_name: str
    user_surname: str
    user_email: str
    