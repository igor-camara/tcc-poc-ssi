from modules.invitation.schema import InvitationRequest
from modules.invitation.service import prepare_receive_invitation_payload, receive_invitation
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/invitation", tags=["invitation"])

@router.post("/receive-url", response_model=SuccessResponse)
async def receive_invitation_url(invitation_request: InvitationRequest):
    invitation_data = await prepare_receive_invitation_payload(invitation_request.alias, invitation_request.url)

    if invitation_data == "INVITATION_PARSE_FAILED":
        return JSONResponse(status_code=400, content={"code": invitation_data, "data": "Failed to parse invitation"})
    if invitation_data == "INVITATION_URL_INVALID":
        return JSONResponse(status_code=400, content={"code": invitation_data, "data": "Invalid invitation URL"})
    if invitation_data == "INVITATION_DATA_NOT_FOUND":
        return JSONResponse(status_code=400, content={"code": invitation_data, "data": "No invitation data found"})
    if invitation_data == "INVITATION_PROCESSING_FAILED":
        return JSONResponse(status_code=400, content={"code": invitation_data, "data": "Failed to process invitation"})
    if invitation_data == "INVITATION_DECODE_FAILED":
        return JSONResponse(status_code=400, content={"code": invitation_data, "data": "Failed to decode invitation"})

    result = await receive_invitation(invitation_data)
    
    if result == "INVITATION_RECEIVE_FAILED":
        return JSONResponse(status_code=500, content={"code": result, "data": "Failed to receive invitation"})

    return JSONResponse(status_code=200, content=SuccessResponse(data="Conexão criada com sucesso").model_dump())