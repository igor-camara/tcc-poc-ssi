from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SchemaCreate(BaseModel):
    schema_id: str = Field(..., description="ID do schema criado pelo issuer")


class SchemaResponse(BaseModel):
    id: str
    schema_id: str
    client_id: str
    created_at: datetime


class SchemaListItem(BaseModel):
    id: str
    schema_id: str
    issuer_name: str
    credential_name: str
    credential_version: str
    created_at: datetime


class SchemaListResponse(BaseModel):
    items: List[SchemaListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
