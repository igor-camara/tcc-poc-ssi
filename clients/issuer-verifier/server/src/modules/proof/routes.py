from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/proof", tags=["proof"])

@router.post("/proof", response_model=SuccessResponse)
def create_invitation_url(alias: str):
    return JSONResponse(status_code=200, content=SuccessResponse(data={"alias": alias}).model_dump())