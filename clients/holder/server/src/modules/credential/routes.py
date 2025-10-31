from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.credential.service import get_holder_credentials, get_offers, accept_offer

router = APIRouter(prefix="/credential", tags=["credential"])

@router.get("/offers", response_model=SuccessResponse)
def list_credential_offers():
    offers = get_offers()
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=offers or []).model_dump()
    )

@router.get("/my-credentials", response_model=SuccessResponse)
def list_holder_credentials(did: str):
    credentials = get_holder_credentials(did)
    
    if isinstance(credentials, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=credentials,
                data="Falha ao recuperar as credenciais"
            ).model_dump()
        )
        
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=credentials).model_dump()
    )

@router.post("/accept-offer", response_model=SuccessResponse)
async def accept_credential_offer(request: Request):
    body = await request.json()
    cred_ex_id = body.get("cred_ex_id")

    if not cred_ex_id:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                code="invalid_request",
                data="cred_ex_id is required"
            ).model_dump()
        )

    result = accept_offer(cred_ex_id)

    if result == "OFFER_ACCEPTANCE_FAILED":
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code="offer_acceptance_failed",
                data="Failed to accept the credential offer"
            ).model_dump()
        )
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=result).model_dump()
    )
