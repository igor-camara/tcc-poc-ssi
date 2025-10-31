from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LedgerRegisterRequest(BaseModel):
    key: str


class LedgerRegisterResponse(BaseModel):
    id: int
    client_id: str
    did: str
    verkey: str
    acapy_admin_url: str
    role: str
    alias: str
    ledger_status: str
    created_at: str
