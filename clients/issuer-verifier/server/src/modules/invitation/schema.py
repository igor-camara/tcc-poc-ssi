from pydantic import BaseModel, Field

class InvitationRequest(BaseModel):
    alias: str = Field(..., example="My Connection")
