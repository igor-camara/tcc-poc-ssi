from pydantic import BaseModel, Field

class InvitationRequest(BaseModel):
    alias: str = Field(..., example="My Connection")

class ConnectionResponse(BaseModel):
    label: str = Field(..., example="My Connection")
    invitation_url: str = Field(..., example="https://example.com/invite?c_i=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ...")