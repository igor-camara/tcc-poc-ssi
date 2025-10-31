from pydantic import BaseModel
from typing import Dict, Optional


class RequestedAttribute(BaseModel):
    cred_id: str
    revealed: bool


class RequestedPredicate(BaseModel):
    cred_id: str


class IndyProof(BaseModel):
    requested_attributes: Dict[str, RequestedAttribute]
    requested_predicates: Optional[Dict[str, RequestedPredicate]] = {}
    self_attested_attributes: Optional[Dict[str, str]] = {}


class SendPresentationRequest(BaseModel):
    indy: IndyProof
