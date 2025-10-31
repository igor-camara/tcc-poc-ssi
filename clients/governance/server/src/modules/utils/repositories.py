from modules.utils.mongodb import MongoDBRepository, get_mongodb_client
from typing import Dict, Any, List, Optional
from datetime import datetime
import secrets


# ==================== STEWARD REPOSITORY ====================

class StewardRepository(MongoDBRepository):    
    def __init__(self, client):
        super().__init__(client, "stewards")
        # Criar índices para otimização
        self.create_index([("email", 1)], unique=True)
        self.create_index([("organization", 1)])
        self.create_index([("status", 1)])
        self.create_index([("created_at", -1)])
    
    def create_steward(
        self,
        name: str,
        email: str,
        organization: str,
        role: str = "steward",
        status: str = "active"
    ) -> str:
        steward = {
            "name": name,
            "email": email,
            "organization": organization,
            "role": role,
            "status": status,
            "schemas_created": 0,
            "credentials_issued": 0
        }
        return self.insert_one(steward)
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"email": email})
    
    def find_by_organization(self, organization: str) -> List[Dict[str, Any]]:
        return self.find_many({"organization": organization})
    
    def find_active_stewards(self) -> List[Dict[str, Any]]:
        return self.find_many({"status": "active"})
    
    def update_steward_info(
        self,
        steward_id: str,
        data: Dict[str, Any]
    ) -> bool:
        return self.update_by_id(steward_id, {"$set": data})
    
    def increment_schemas_created(self, steward_id: str) -> bool:
        return self.update_by_id(
            steward_id,
            {"$inc": {"schemas_created": 1}}
        )
    
    def increment_credentials_issued(self, steward_id: str) -> bool:
        return self.update_by_id(
            steward_id,
            {"$inc": {"credentials_issued": 1}}
        )
    
    def deactivate_steward(self, steward_id: str) -> bool:
        return self.update_by_id(
            steward_id,
            {"$set": {"status": "inactive"}}
        )
    
    def get_steward_statistics(self) -> Dict[str, int]:
        return {
            "total": self.count(),
            "active": self.count({"status": "active"}),
            "inactive": self.count({"status": "inactive"})
        }


# ==================== CLIENT REPOSITORY ====================

class ClientRepository(MongoDBRepository):
    def __init__(self, client):
        super().__init__(client, "clients")
        self.create_index([("cnpj", 1)], unique=True)
        self.create_index([("email", 1)], unique=True)
        self.create_index([("status", 1)])
        self.create_index([("client_type", 1)])
        self.create_index([("created_at", -1)])
    
    def create_client(
        self,
        company_name: str,
        cnpj: str,
        email: str,
        phone: str,
        address: str,
        client_type: str,
        description: Optional[str] = None,
        status: str = "em_votacao"
    ) -> str:
        client_data = {
            "company_name": company_name,
            "cnpj": cnpj,
            "email": email,
            "phone": phone,
            "address": address,
            "client_type": client_type,
            "description": description,
            "status": status
        }
        return self.insert_one(client_data)
    
    def find_by_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"cnpj": cnpj})
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"email": email})
    
    def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        return self.find_many({"status": status})
    
    def find_by_type(self, client_type: str) -> List[Dict[str, Any]]:
        return self.find_many({"client_type": client_type})
    
    def find_recent_clients(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.find_many(
            sort=[("created_at", -1)],
            limit=limit
        )
    
    def search_clients(self, query: str) -> List[Dict[str, Any]]:
        filter = {
            "$or": [
                {"company_name": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"cnpj": {"$regex": query, "$options": "i"}}
            ]
        }
        return self.find_many(filter)
    
    def update_client_status(self, client_id: str, status: str) -> bool:
        return self.update_by_id(client_id, {"$set": {"status": status, "updated_at": datetime.utcnow()}})
    
    def generate_api_key(self) -> str:
        """Gera uma chave de API segura e única"""
        return f"gov_{secrets.token_urlsafe(32)}"
    
    def set_api_key(self, client_id: str, api_key: str) -> bool:
        """Define a chave de API para um cliente"""
        return self.update_by_id(client_id, {"$set": {"api_key": api_key, "updated_at": datetime.utcnow()}})
    
    def set_first_vote_timestamp(self, client_id: str) -> bool:
        """Define o timestamp do primeiro voto se ainda não existir"""
        client = self.find_by_id(client_id)
        if client and not client.get("first_vote_at"):
            return self.update_by_id(client_id, {"$set": {"first_vote_at": datetime.utcnow()}})
        return False
    
    def update_client_info(
        self,
        client_id: str,
        data: Dict[str, Any]
    ) -> bool:
        data["updated_at"] = datetime.utcnow()
        return self.update_by_id(client_id, {"$set": data})
    
    def get_client_statistics(self) -> Dict[str, Any]:
        return {
            "total": self.count(),
            "em_votacao": self.count({"status": "em_votacao"}),
            "aprovado": self.count({"status": "aprovado"}),
            "rejeitado": self.count({"status": "rejeitado"}),
            "issuers": self.count({"client_type": "issuer"}),
            "verifiers": self.count({"client_type": "verifier"}),
            "both": self.count({"client_type": "both"})
        }


# ==================== SCHEMA REPOSITORY ====================

class SchemaRepository(MongoDBRepository):
    def __init__(self, client):
        super().__init__(client, "schemas")
        # Criar índices
        self.create_index([("schema_id", 1), ("client_id", 1)], unique=True)
        self.create_index([("steward_id", 1)])
        self.create_index([("name", 1)])
        self.create_index([("created_at", -1)])
    
    def create_schema(
        self,
        schema_id: str,
        name: str,
        version: str,
        attributes: List[str],
        steward_id: str
    ) -> str:
        schema = {
            "schema_id": schema_id,
            "name": name,
            "version": version,
            "attributes": attributes,
            "steward_id": steward_id,
            "credentials_issued": 0
        }
        return self.insert_one(schema)
    
    def find_by_schema_id(self, schema_id: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"schema_id": schema_id})
    
    def find_by_steward(self, steward_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"steward_id": steward_id})
    
    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        return self.find_many({"name": {"$regex": name, "$options": "i"}})
    
    def increment_credentials_issued(self, schema_id: str) -> bool:
        return self.update_one(
            {"schema_id": schema_id},
            {"$inc": {"credentials_issued": 1}}
        )


# ==================== CREDENTIAL REPOSITORY ====================

class CredentialRepository(MongoDBRepository):
    def __init__(self, client):
        super().__init__(client, "credentials")
        # Criar índices
        self.create_index([("credential_id", 1)], unique=True)
        self.create_index([("client_id", 1)])
        self.create_index([("steward_id", 1)])
        self.create_index([("schema_id", 1)])
        self.create_index([("status", 1)])
        self.create_index([("created_at", -1)])
    
    def create_credential(
        self,
        credential_id: str,
        schema_id: str,
        steward_id: str,
        client_id: str,
        attributes: Dict[str, Any],
        status: str = "active"
    ) -> str:
        credential = {
            "credential_id": credential_id,
            "schema_id": schema_id,
            "steward_id": steward_id,
            "client_id": client_id,
            "attributes": attributes,
            "status": status,
            "issued_at": datetime.utcnow()
        }
        return self.insert_one(credential)
    
    def find_by_credential_id(self, credential_id: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"credential_id": credential_id})
    
    def find_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"client_id": client_id})
    
    def find_by_steward(self, steward_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"steward_id": steward_id})
    
    def find_by_schema(self, schema_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"schema_id": schema_id})
    
    def revoke_credential(self, credential_id: str) -> bool:
        return self.update_one(
            {"credential_id": credential_id},
            {"$set": {"status": "revoked", "revoked_at": datetime.utcnow()}}
        )
    
    def get_credential_statistics(self) -> Dict[str, int]:
        return {
            "total": self.count(),
            "active": self.count({"status": "active"}),
            "revoked": self.count({"status": "revoked"})
        }


# ==================== VOTE REPOSITORY ====================

class TruthyRepository(MongoDBRepository):
    def __init__(self, client):
        super().__init__(client, "truthys")
        self.create_index([("client_id", 1)], unique=True)
        self.create_index([("did", 1)], unique=True)
        self.create_index([("created_at", -1)])
    
    def create_truthy(
        self,
        client_id: str,
        did: str,
        verkey: str,
        acapy_admin_url: str,
        role: str,
        alias: str,
        ledger_status: str = "pending"
    ) -> str:
        truthy_data = {
            "client_id": client_id,
            "did": did,
            "verkey": verkey,
            "acapy_admin_url": acapy_admin_url,
            "role": role,
            "alias": alias,
            "ledger_status": ledger_status
        }
        return self.insert_one(truthy_data)
    
    def find_by_client_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"client_id": client_id})
    
    def find_by_did(self, did: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"did": did})
    
    def update_ledger_status(self, truthy_id: str, status: str) -> bool:
        return self.update_by_id(truthy_id, {"$set": {"ledger_status": status, "updated_at": datetime.utcnow()}})


class VoteRepository(MongoDBRepository):
    def __init__(self, client):
        super().__init__(client, "votes")
        self.create_index([("client_id", 1)])
        self.create_index([("steward_id", 1)])
        self.create_index([("created_at", -1)])
        self.create_index([("steward_id", 1), ("client_id", 1)], unique=True)
    
    def create_vote(
        self,
        steward_id: str,
        client_id: str,
        vote: str,
        comment: Optional[str] = None
    ) -> str:
        vote_data = {
            "steward_id": steward_id,
            "client_id": client_id,
            "vote": vote,
            "comment": comment
        }
        return self.insert_one(vote_data)
    
    def find_by_client(self, client_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"client_id": client_id})
    
    def find_by_steward(self, steward_id: str) -> List[Dict[str, Any]]:
        return self.find_many({"steward_id": steward_id})
    
    def find_vote(self, steward_id: str, client_id: str) -> Optional[Dict[str, Any]]:
        return self.find_one({"steward_id": steward_id, "client_id": client_id})
    
    def count_votes_by_client(self, client_id: str) -> Dict[str, int]:
        votes = self.find_by_client(client_id)
        approve_count = sum(1 for v in votes if v.get("vote") == "approve")
        reject_count = sum(1 for v in votes if v.get("vote") == "reject")
        abstain_count = sum(1 for v in votes if v.get("vote") == "abstain")
        return {
            "total": len(votes),
            "approve": approve_count,
            "reject": reject_count,
            "abstain": abstain_count
        }
