from pydantic import BaseModel, Field

class CredentialRequest(BaseModel):
    name: str = Field(..., description="Name of the schema")
    version: str = Field(..., description="Version of the schema")
    attributes: list[str] = Field(..., description="List of attribute names")