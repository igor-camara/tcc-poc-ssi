import modules.ledger.service as ledger_service
from modules.utils.model import ErrorResponse, SuccessResponse
from modules.ledger.schemas import LedgerRegisterRequest
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter(prefix="/ledger", tags=["ledger"])


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
