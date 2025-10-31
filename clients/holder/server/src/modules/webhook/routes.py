from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse
from fastapi import Request
from modules.webhook.service import process_issue_credential_v2_0, process_present_proof_v2_0

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/topic/{topic}/", response_model=SuccessResponse)
async def webhook(topic: str, request: Request):
    body = await request.json()

    if topic == "issue_credential_v2_0":
        process_issue_credential_v2_0(body)

    if topic == "present_proof_v2_0":
        process_present_proof_v2_0(body)

    return JSONResponse(status_code=200, content=SuccessResponse(data=f"Webhook recebido com sucesso para o tópico {topic}").model_dump())
