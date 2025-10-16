from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class HolderCredentialRecord(BaseModel):
    credential_exchange_id: str = Field(..., description="ID da troca de credencial")
    credential_id: Optional[str] = Field(None, description="ID da credencial armazenada")
    credential_name: str = Field(..., description="Nome/descrição da credencial")
    credential_definition_id: str = Field(..., description="ID da definição da credencial")
    schema_id: Optional[str] = Field(None, description="ID do schema da credencial")
    issuer_did: Optional[str] = Field(None, description="DID do emissor")
    issuer_alias: Optional[str] = Field(None, description="Alias/nome do emissor")
    issued_at: Optional[str] = Field(None, description="Data e hora da emissão")
    received_at: Optional[str] = Field(None, description="Data e hora do recebimento")
    status: str = Field(..., description="Status da credencial (credential-issued, done, etc)")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Atributos da credencial")
    version: Optional[str] = Field(None, description="Versão do schema")
    is_valid: bool = Field(default=True, description="Se a credencial é válida")
