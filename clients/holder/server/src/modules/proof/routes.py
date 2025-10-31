from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.proof.service import (
    get_proof_requests, 
    get_proof_request_by_id, 
    get_credentials_for_proof_request,
    send_presentation
)

router = APIRouter(prefix="/proof", tags=["proof"])

@router.get("/requests", response_model=SuccessResponse)
def list_proof_requests():
    proof_requests = get_proof_requests()
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=proof_requests or []).model_dump()
    )

@router.get("/requests/{pres_ex_id}", response_model=SuccessResponse)
def get_proof_request(pres_ex_id: str):
    proof_request = get_proof_request_by_id(pres_ex_id)
    
    if not proof_request:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                code="NOT_FOUND",
                data=f"Proof request with pres_ex_id {pres_ex_id} not found"
            ).model_dump()
        )
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=proof_request).model_dump()
    )

@router.get("/requests/{pres_ex_id}/credentials", response_model=SuccessResponse)
def get_credentials_for_request(pres_ex_id: str):
    """Get available credentials for a proof request"""
    credentials = get_credentials_for_proof_request(pres_ex_id)
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=credentials or []).model_dump()
    )

@router.post("/requests/{pres_ex_id}/send-presentation", response_model=SuccessResponse)
async def send_proof_presentation(pres_ex_id: str, request: Request):
    body = await request.json()
    
    proof_request = get_proof_request_by_id(pres_ex_id)
    if not proof_request:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                code="NOT_FOUND",
                data=f"Proof request with pres_ex_id {pres_ex_id} not found"
            ).model_dump()
        )
    
    result = send_presentation(pres_ex_id, body)
    
    if isinstance(result, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=result,
                data="Falha ao enviar apresentação"
            ).model_dump()
        )
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=result).model_dump()
    )
