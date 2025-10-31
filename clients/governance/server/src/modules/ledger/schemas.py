from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LedgerRegisterRequest(BaseModel):
    did: str = Field(..., description="DID criado localmente pelo cliente")
    verkey: str = Field(..., description="Chave pública correspondente ao DID")
    acapy_admin_url: str = Field(..., description="URL do ACA-Py do cliente")

class LedgerRegisterResponse(BaseModel):
    id: str
    client_id: str
    did: str
    verkey: str
    acapy_admin_url: str
    role: str
    alias: str
    ledger_status: str
    created_at: datetime
