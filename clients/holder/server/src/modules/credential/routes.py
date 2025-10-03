from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.credential.service import get_holder_credentials

router = APIRouter(prefix="/credential", tags=["credential"])

@router.get("/my-credentials", response_model=SuccessResponse)
async def list_holder_credentials():
    """
    Lista todas as credenciais que o Holder possui.
    
    Retorna informações sobre:
    - Quem emitiu a credencial (issuer_did, issuer_alias)
    - Quando a credencial foi emitida (issued_at)
    - Nome/Descrição da credencial (credential_name)
    - Detalhes da credencial (attributes, version)
    - Status da credencial (status, is_valid)
    """
    credentials = await get_holder_credentials()
    
    if isinstance(credentials, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=credentials,
                data="Falha ao recuperar as credenciais"
            ).model_dump()
        )
    
    # Converte os modelos Pydantic para dicionários
    credentials_data = [cred.model_dump() for cred in credentials]
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=credentials_data).model_dump()
    )