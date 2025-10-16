from pydantic import BaseModel, Field

class ConnectionResponse(BaseModel):
    alias: str = Field(..., description="Alias of the connection")
    connection_id: str = Field(..., description="ID of the connection")
    created_at: str = Field(..., description="Creation timestamp")
    invitation_key: str = Field(..., description="Invitation key")
    invitation_mode: str = Field(..., description="Invitation mode")
    state: str = Field(..., description="State of the connection")