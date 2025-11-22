import modules.ledger.service as ledger_service
from modules.utils.model import ErrorResponse, SuccessResponse
from modules.ledger.schemas import LedgerRegisterRequest
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

from modules.config.settings import settings
import httpx
from fastapi import Request
from modules.client.service import AcaPyClient

router = APIRouter(prefix="/ledger", tags=["ledger"])

@router.get("/schemas/{schema_id:path}")
def get_schema_details(schema_id: str):
    """
    Obtém os detalhes de um schema específico da ledger
    
    Args:
        schema_id: ID do schema no formato DID:2:nome:versão
        
    Returns:
        Detalhes do schema incluindo atributos (attrNames)
    """
    try:
        schema = AcaPyClient.schemas.get_schema(id=schema_id)
        
        if schema:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=SuccessResponse(data=schema).model_dump()
            )
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                code="SCHEMA_NOT_FOUND",
                data=f"Schema {schema_id} não encontrado"
            ).model_dump()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code="INTERNAL_SERVER_ERROR",
                data=str(e)
            ).model_dump()
        )

@router.get("/schemas-redirect")
async def schemas_redirect(request: Request):
    try:
        base_url = f"{settings.governance_url}/api/schemas"
        query_params = str(request.query_params)
        url = base_url
        if query_params:
            url += f"?{query_params}"

        headers = {"X-API-Key": settings.governance_api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/register", response_model=SuccessResponse)
def register_did(request: LedgerRegisterRequest):
    try:
        result = ledger_service.register_did_on_governance(request.key)
        
        if "error" in result:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    code="REGISTRATION_FAILED", 
                    data=result["error"]
                ).model_dump()
            )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content=SuccessResponse(data=result).model_dump()
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code="INTERNAL_SERVER_ERROR", 
                data=str(e)
            ).model_dump()
        )


@router.get("/check-key", response_model=SuccessResponse)
def check_governance_key():
    try:
        result = ledger_service.check_governance_key()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content=SuccessResponse(data=result).model_dump()
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code="INTERNAL_SERVER_ERROR", 
                data=str(e)
            ).model_dump()
        )
