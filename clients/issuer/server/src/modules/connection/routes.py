from fastapi import APIRouter
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from modules.connection.service import get_connections

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