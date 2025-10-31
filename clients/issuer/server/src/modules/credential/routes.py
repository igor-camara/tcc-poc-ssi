from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.credential.schema import CreateCredentialRequest, CredentialOfferRequest
from modules.credential.service import (
    create_schema, 
    create_credential_definition, 
    list_ledger_credentials, 
    get_credential_by_id,
    get_credential_definition_by_schema_id,
    send_credential_offer,
    get_connection_by_id,
    get_issued_credentials,
    issue_credential
)

router = APIRouter(prefix="/credential", tags=["credential"])

@router.post("/create", response_model=SuccessResponse)
def create_credential(credential: CreateCredentialRequest):
    schema = create_schema(
        schema_name=credential.name,
        schema_version=credential.version,
        attributes=credential.attributes
    )

    if isinstance(schema, str) or not schema:
        return JSONResponse(status_code=400, content=ErrorResponse(code=schema, data="Schema creation failed").model_dump())

    cred_def = create_credential_definition(
        schema_id=schema['schema_id'],
        support_revocation=False
    )

    if isinstance(cred_def, str) or not cred_def:
        return JSONResponse(status_code=400, content=ErrorResponse(code=cred_def, data="Credential definition creation failed").model_dump())

    return JSONResponse(status_code=200, content=SuccessResponse(data="Credential creation successful").model_dump())

@router.get("", response_model=SuccessResponse)
def get_credentials():
    credentials = list_ledger_credentials()
    return JSONResponse(status_code=200, content=SuccessResponse(data=credentials).model_dump())

@router.post("/offer", response_model=SuccessResponse)
def offer_credential(offer_request: CredentialOfferRequest):
    connection = get_connection_by_id(offer_request.connection_id)
    if not connection:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(code="connection_not_found", data="Connection not found").model_dump()
        )
    
    schema = get_credential_by_id(offer_request.schema_id)
    if not schema:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(code="credential_not_found", data="Credential not found").model_dump()
        )

    cred_def = get_credential_definition_by_schema_id(schema['id'])
    if not cred_def:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(code="cred_def_not_found", data="Credential definition not found").model_dump()
        )

    offer_result = send_credential_offer(
        connection_id=offer_request.connection_id,
        cred_def_id=cred_def[0]['id'],
        schema_id=offer_request.schema_id,
        attributes=offer_request.attributes
    )

    if isinstance(offer_result, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(code=offer_result, data="Failed to send credential offer").model_dump()
        )
    return JSONResponse(status_code=200, content=SuccessResponse(data="Offer creation successful").model_dump())

@router.get("/issued", response_model=SuccessResponse)
def get_issued_credentials_list():
    issued_credentials = get_issued_credentials()

    if isinstance(issued_credentials, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code="issued_credentials_retrieval_failed",
                data=issued_credentials
            ).model_dump()
        )

    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=issued_credentials).model_dump()
    )

@router.post("/issue/{cred_ex_id}/", response_model=SuccessResponse)
def credential_issue(cred_ex_id: str):
    result = issue_credential(cred_ex_id=cred_ex_id)

    if isinstance(result, str):
        return JSONResponse(status_code=500, content=ErrorResponse(code=result, data="Credential issuance failed").model_dump())
    
    return JSONResponse(status_code=200, content=SuccessResponse(data="Credential issued successfully").model_dump())