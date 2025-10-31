from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse
from modules.proof import service

router = APIRouter(prefix="/proof", tags=["proof"])

@router.post("", response_model=SuccessResponse)
def create_proof_request(proof_request: dict):
    result = service.create_proof_request(proof_request)
    if isinstance(result, dict) and result.get("error"):
        return JSONResponse(status_code=400, content={"code": "ERROR", "data": result["error"]})
    return JSONResponse(status_code=200, content=SuccessResponse(data="Proof request creation successful").model_dump())

@router.get("", response_model=SuccessResponse)
def get_all_proofs(
    descending: bool = Query(False, description="Ordenar de forma descendente"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação")
):
    result = service.get_all_proofs(descending=descending, limit=limit, offset=offset)
    if result is None:
        return JSONResponse(status_code=500, content={"code": "ERROR", "data": "Failed to retrieve proofs"})
    return JSONResponse(status_code=200, content=SuccessResponse(data=result).model_dump())

@router.get("/{pres_ex_id}", response_model=SuccessResponse)
def get_proof_by_id(pres_ex_id: str):
    result = service.get_proof_by_id(pres_ex_id)
    if result is None:
        return JSONResponse(status_code=404, content={"code": "ERROR", "data": "Proof not found"})
    return JSONResponse(status_code=200, content=SuccessResponse(data=result).model_dump())

