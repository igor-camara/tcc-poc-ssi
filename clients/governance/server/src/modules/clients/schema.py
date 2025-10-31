from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, List
from datetime import datetime

class ClientCreate(BaseModel):
    company_name: str = Field(..., description="Nome da empresa cliente")
    cnpj: str = Field(..., description="CNPJ da empresa", pattern=r'^\d{14}$')
    email: EmailStr = Field(..., description="Email de contato")
    phone: str = Field(..., description="Telefone de contato")
    address: str = Field(..., description="Endereço completo")
    client_type: Literal["issuer", "verifier", "both"] = Field(..., description="Tipo de cliente no fluxo SSI")
    description: Optional[str] = Field(None, description="Descrição/justificativa da solicitação")

class ClientResponse(BaseModel):
    id: str
    company_name: str
    cnpj: str
    email: str
    phone: str
    address: str
    client_type: str
    description: Optional[str]
    status: str
    api_key: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ClientListResponse(BaseModel):
    id: str
    company_name: str
    cnpj: str
    email: str
    client_type: str
    status: str
    api_key: Optional[str] = None
    created_at: datetime

class ClientVoteDetail(BaseModel):
    id: str
    steward_id: str
    steward_name: str
    vote: str
    comment: Optional[str]
    created_at: datetime

class ClientVotingResponse(BaseModel):
    client_id: str
    client_name: str
    status: str
    total_votes: int
    approve_votes: int
    reject_votes: int
    abstain_votes: int
    first_vote_at: Optional[datetime]
    voting_deadline: Optional[datetime]
    votes: List[ClientVoteDetail]
