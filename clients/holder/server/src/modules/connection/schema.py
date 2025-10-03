from pydantic import BaseModel, Field
from typing import List, Optional

class ConnectionResponse(BaseModel):
    alias: str = Field(..., description="Alias of the connection")
    connection_id: str = Field(..., description="ID of the connection")
    created_at: str = Field(..., description="Creation timestamp")
    invitation_key: str = Field(..., description="Invitation key")
    invitation_mode: str = Field(..., description="Invitation mode")
    state: str = Field(..., description="State of the connection")

class VerificationMethod(BaseModel):
    id: str = Field(..., description="ID do método de verificação")
    type: str = Field(..., description="Tipo do método de verificação")
    controller: str = Field(..., description="DID do controlador")
    publicKeyBase58: Optional[str] = Field(None, description="Chave pública em Base58")

class Service(BaseModel):
    id: str = Field(..., description="ID do serviço")
    type: str = Field(..., description="Tipo do serviço")
    serviceEndpoint: str = Field(..., description="Endpoint do serviço")
    recipientKeys: Optional[List[str]] = Field(None, description="Chaves dos destinatários")
    routingKeys: Optional[List[str]] = Field(None, description="Chaves de roteamento")

class DIDDocumentResponse(BaseModel):
    context: List[str] = Field(..., alias="@context", description="Contexto do documento DID")
    id: str = Field(..., description="DID")
    verificationMethod: List[VerificationMethod] = Field(..., description="Métodos de verificação")
    authentication: List[str] = Field(..., description="Métodos de autenticação")
    assertionMethod: Optional[List[str]] = Field(None, description="Métodos de asserção")
    service: Optional[List[Service]] = Field(None, description="Serviços associados ao DID")
    
    class Config:
        populate_by_name = True