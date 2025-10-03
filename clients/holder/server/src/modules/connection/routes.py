from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.connection.service import get_connections, get_did_document

router = APIRouter(prefix="/connection", tags=["connection"])

@router.get("/all", response_model=SuccessResponse)
async def list_connections():
    connections = await get_connections(state="invitation")
    
    if isinstance(connections, str):
        return JSONResponse(
            status_code=500, 
            content=ErrorResponse(code=connections, data="Failed to retrieve connections").model_dump()
        )
    
    return JSONResponse(status_code=200, content=SuccessResponse(data=connections).model_dump())

@router.get("/did_document/{did}", response_model=SuccessResponse)
async def retrieve_did_document(did: str):
    did_document = await get_did_document(did)
    
    if isinstance(did_document, str):
        error_messages = {
            "DID_NOT_FOUND": "DID não encontrado na wallet ou no ledger",
            "DID_DOCUMENT_RETRIEVAL_FAILED": "Falha ao recuperar o DID Document"
        }
        
        return JSONResponse(
            status_code=404 if did_document == "DID_NOT_FOUND" else 500,
            content=ErrorResponse(
                code=did_document,
                data=error_messages.get(did_document, "Erro desconhecido")
            ).model_dump()
        )
    
    return JSONResponse(
        status_code=200,
        content=SuccessResponse(data=did_document).model_dump(by_alias=True)
    )