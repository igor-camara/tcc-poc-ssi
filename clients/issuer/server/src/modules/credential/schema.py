from pydantic import BaseModel, Field
from modules.utils.model import SuccessResponse
from typing import Dict, Any

class CreateCredentialRequest(BaseModel):
    name: str = Field(..., description="Name of the schema")
    version: str = Field(..., description="Version of the schema")
    attributes: list[str] = Field(..., description="List of attribute names")

class CredentialDetail(BaseModel):
    id: str = Field(..., description="ID of the credential")
    name: str = Field(..., description="Name of the credential")
    version: str = Field(..., description="Version of the credential")
    attrNames: list[str] = Field(..., description="List of attribute names")

class CredentialOfferRequest(BaseModel):
    connection_id: str = Field(..., description="Connection ID with the holder")
    cred_def_id: str = Field(..., description="Credential definition ID")
    attributes: Dict[str, Any] = Field(..., description="Credential attributes as key-value pairs")
    comment: str = Field(default="", description="Optional comment for the credential offer")
