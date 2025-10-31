from typing import Dict, Any, List, Optional
from modules.utils.repositories import SchemaRepository, ClientRepository
from modules.utils.mongodb import get_mongodb_client
from datetime import datetime
from bson import ObjectId
import math


class SchemaService:
    def __init__(self):
        self.db_client = get_mongodb_client()
        self.schema_repository = SchemaRepository(self.db_client)
        self.client_repository = ClientRepository(self.db_client)
    
    def register_schema(self, client_id: str, schema_id: str) -> Dict[str, Any]:
        existing_schema = self.schema_repository.find_one({"schema_id": schema_id, "client_id": client_id})
        if existing_schema:
            raise ValueError("Schema já registrado para este cliente")
        
        schema_data = {
            "schema_id": schema_id,
            "client_id": client_id,
            "created_at": datetime.utcnow()
        }
        
        schema_obj_id = self.schema_repository.insert_one(schema_data)
        
        created_schema = self.schema_repository.find_by_id(schema_obj_id)
        
        return {
            "id": str(created_schema["_id"]),
            "schema_id": created_schema["schema_id"],
            "client_id": created_schema["client_id"],
            "created_at": created_schema["created_at"]
        }
    
    def parse_schema_id(self, schema_id: str) -> Dict[str, str]:
        try:
            parts = schema_id.split(":")
            if len(parts) >= 4:
                credential_name = ":".join(parts[2:-1])
                credential_version = parts[-1]
            else:
                credential_name = schema_id
                credential_version = "N/A"
            
            return {
                "credential_name": credential_name,
                "credential_version": credential_version
            }
        except Exception:
            return {
                "credential_name": schema_id,
                "credential_version": "N/A"
            }
    
    def get_schemas(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        all_schemas = self.schema_repository.find_many({}, sort=[("created_at", -1)])
        
        schemas_with_details = []
        for schema in all_schemas:
            client = self.client_repository.find_by_id(schema["client_id"])
            if not client:
                continue
            
            parsed = self.parse_schema_id(schema["schema_id"])
            
            issuer_name = client.get("company_name", "")
            credential_name = parsed["credential_name"]
            
            if search:
                search_lower = search.lower()
                if (search_lower not in issuer_name.lower() and 
                    search_lower not in credential_name.lower()):
                    continue
            
            schemas_with_details.append({
                "id": str(schema["_id"]),
                "schema_id": schema["schema_id"],
                "issuer_name": issuer_name,
                "credential_name": credential_name,
                "credential_version": parsed["credential_version"],
                "created_at": schema["created_at"]
            })
        
        total = len(schemas_with_details)
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = schemas_with_details[start_idx:end_idx]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }


schema_service = SchemaService()
