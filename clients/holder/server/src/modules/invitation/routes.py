from modules.invitation.schema import InvitationRequest
from modules.invitation.service import receive
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/receive-url", response_model=SuccessResponse)
def receive_invitation_url(invitation_request: InvitationRequest):
    result = receive(invitation_request.alias, invitation_request.url, invitation_request.user_did)
    
    if result == "INVITATION_RECEIVE_FAILED":
        return JSONResponse(status_code=500, content={"code": result, "data": "Failed to receive invitation"})

    return JSONResponse(status_code=200, content=SuccessResponse(data="Conexão criada com sucesso").model_dump())