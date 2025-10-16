from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.connection.service import get_connections, get_did_document

router = APIRouter(prefix="/connections", tags=["connection"])

@router.get("", response_model=SuccessResponse)
def list_connections(alias: str = None, id: str = None):
    connections = get_connections(alias=alias, id=id)
    
    if isinstance(connections, str):
        return JSONResponse(
            status_code=500, 
            content=ErrorResponse(code=connections, data="Failed to retrieve connections").model_dump()
        )
    return JSONResponse(status_code=200, content=SuccessResponse(data=connections).model_dump())

@router.get("/did-document", response_model=SuccessResponse)
def did_document(did: str):
    did_document = get_did_document(did=did)

    if isinstance(did_document, str):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(code=did_document, data="Failed to retrieve DID document").model_dump()
        )
    return JSONResponse(status_code=200, content=SuccessResponse(data=did_document).model_dump())
