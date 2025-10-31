from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

class StewardCreate(BaseModel):
    name: str = Field(..., description="Nome do steward")
    email: EmailStr = Field(..., description="Email do steward")
    organization: str = Field(..., description="Organização do steward")
    role: str = Field(default="steward", description="Papel do steward")

class StewardResponse(BaseModel):
    id: str
    name: str
    email: str
    organization: str
    role: str
    status: str
    schemas_created: int
    credentials_issued: int
    created_at: datetime

class StewardListResponse(BaseModel):
    id: str
    name: str
    email: str
    organization: str
    status: str
    created_at: datetime

class VoteCreate(BaseModel):
    steward_id: str = Field(..., description="ID do steward votante")
    client_id: str = Field(..., description="ID do cliente sendo votado")
    vote: Literal["approve", "reject", "abstain"] = Field(..., description="Voto do steward")
    comment: Optional[str] = Field(None, description="Comentário do voto")

class VoteResponse(BaseModel):
    id: str
    steward_id: str
    client_id: str
    vote: str
    comment: Optional[str]
    created_at: datetime
