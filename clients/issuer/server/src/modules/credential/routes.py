from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.credential.schema import CredentialRequest
from modules.credential.service import create_schema, create_credential_definition

router = APIRouter(prefix="/credential", tags=["credential"])

@router.post("/create", response_model=SuccessResponse)
async def create_credential(credential: CredentialRequest):
    schema = await create_schema(
        schema_name=credential.name,
        schema_version=credential.version,
        attributes=credential.attributes
    )

    if isinstance(schema, str) or not schema:
        return JSONResponse(status_code=400, content=ErrorResponse(code=schema, data="Schema creation failed").model_dump())

    cred_def = await create_credential_definition(
        schema_id=schema['sent']['schema']['id'],
        support_revocation=False
    )

    if isinstance(cred_def, str) or not cred_def:
        return JSONResponse(status_code=400, content=ErrorResponse(code=cred_def, data="Credential definition creation failed").model_dump())

    return JSONResponse(status_code=200, content=SuccessResponse(data="Credential creation successful").model_dump())

@router.post("/offer")
async def offer_credential():
    return JSONResponse(status_code=200, content=SuccessResponse(data="Credential offer successful").model_dump())

@router.post("/issue")
async def issue_credential():
    return JSONResponse(status_code=200, content=SuccessResponse(data="Credential issuance successful").model_dump())