from pydantic import BaseModel, Field
from modules.utils.model import SuccessResponse

class CreateCredentialRequest(BaseModel):
    name: str = Field(..., description="Name of the schema")
    version: str = Field(..., description="Version of the schema")
    attributes: list[str] = Field(..., description="List of attribute names")

class CredentialDetail(BaseModel):
    id: str = Field(..., description="ID of the credential")
    name: str = Field(..., description="Name of the credential")
    version: str = Field(..., description="Version of the credential")
    attrNames: list[str] = Field(..., description="List of attribute names")
    