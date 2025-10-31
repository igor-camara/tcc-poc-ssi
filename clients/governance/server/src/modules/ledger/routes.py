from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from modules.ledger.schemas import LedgerRegisterRequest, LedgerRegisterResponse
from modules.ledger.service import ledger_service
from modules.utils.model import SuccessResponse
from modules.utils.repositories import ClientRepository
from modules.utils.mongodb import get_mongodb_client

router = APIRouter(prefix="/ledger", tags=["ledger"])

def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header é obrigatório"
        )
    
    db_client = get_mongodb_client()
    client_repository = ClientRepository(db_client)
    
    client = client_repository.find_one({"api_key": x_api_key})
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    
    if client.get("status") != "aprovado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente não está aprovado"
        )
    
    return str(client["_id"])

@router.post("/register", response_model=SuccessResponse[LedgerRegisterResponse], status_code=status.HTTP_201_CREATED)
async def register_client_on_ledger(
    register_data: LedgerRegisterRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    try:
        client_id = validate_api_key(x_api_key)
        
        if not register_data.did or not register_data.verkey or not register_data.acapy_admin_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="did, verkey e acapy_admin_url são obrigatórios"
            )
        
        result = await ledger_service.register_client_did(client_id, register_data)
        return SuccessResponse(data=result)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar cliente na ledger: {str(e)}"
        )
