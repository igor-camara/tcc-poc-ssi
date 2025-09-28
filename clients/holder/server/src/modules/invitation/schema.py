from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class InvitationRequest(BaseModel):
    alias: str = Field(..., example="My Connection")
    url: str = Field(..., example="https://example.com/invitation?token=abc123")
