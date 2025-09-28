from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AuthHeaders(BaseModel):
    token: Optional[str] = Field(None, example="Bearer your_jwt_token_here", alias="authorization")
    did: Optional[str] = Field(None, example="did:example:123456789abcdefghi", alias="x-did")
    verkey: Optional[str] = Field(None, example="your_verification_key_here", alias="x-verkey")