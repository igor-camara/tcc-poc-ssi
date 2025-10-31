from typing import Optional
from modules.utils.mongodb import get_mongodb_client
from modules.utils.repositories import TruthyRepository, ClientRepository
from modules.ledger.schemas import LedgerRegisterRequest, LedgerRegisterResponse
from modules.config.settings import settings
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import httpx

class LedgerService:
    def __init__(self):
        self.db_client = get_mongodb_client()
        self.truthy_repository = TruthyRepository(self.db_client)
        self.client_repository = ClientRepository(self.db_client)
        self.endorser_admin_url = settings.admin_url
        self.endorser_api_key = settings.api_key
    
    def _convert_to_response(self, truthy_data: dict) -> LedgerRegisterResponse:
        truthy_data["id"] = str(truthy_data.pop("_id"))
        truthy_data["client_id"] = str(truthy_data["client_id"])
        return LedgerRegisterResponse(**truthy_data)
    
    async def register_on_ledger(self, did: str, verkey: str, alias: str, role: str) -> dict:
        url = f"{self.endorser_admin_url}/ledger/register-nym"
        headers = {"X-API-Key": self.endorser_api_key}
        payload = {
            "did": did,
            "verkey": verkey,
            "alias": alias,
            "role": role
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def register_client_did(self, client_id: str, register_data: LedgerRegisterRequest) -> LedgerRegisterResponse:
        client = self.client_repository.find_by_id(client_id)
        if not client:
            raise ValueError("Cliente não encontrado")
        
        if client.get("status") != "aprovado":
            raise ValueError("Cliente não está aprovado")
        
        existing_truthy = self.truthy_repository.find_by_client_id(client_id)
        if existing_truthy:
            raise ValueError("Cliente já possui DID registrado")
        
        existing_did = self.truthy_repository.find_by_did(register_data.did)
        if existing_did:
            raise ValueError("DID já registrado no sistema")
        
        client_type = client.get("client_type")
        if client_type == "issuer" or client_type == "both":
            role = "ENDORSER"
        else:
            role = "NONE"
        
        alias = client.get("company_name", "Client")
        
        try:
            await self.register_on_ledger(
                did=register_data.did,
                verkey=register_data.verkey,
                alias=alias,
                role=role
            )
            
            truthy_id = self.truthy_repository.create_truthy(
                client_id=client_id,
                did=register_data.did,
                verkey=register_data.verkey,
                acapy_admin_url=register_data.acapy_admin_url,
                role=role,
                alias=alias,
                ledger_status="registered"
            )
            
            created_truthy = self.truthy_repository.find_by_id(truthy_id)
            return self._convert_to_response(created_truthy)
        
        except DuplicateKeyError:
            raise ValueError("Registro já existe no sistema")
        except Exception as e:
            raise ValueError(f"Erro ao registrar na ledger: {str(e)}")

ledger_service = LedgerService()
