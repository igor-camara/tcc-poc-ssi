from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from modules.utils.model import SuccessResponse, ErrorResponse
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["notification"])

class UpdateReadStatusRequest(BaseModel):
    read: bool

@router.get("", response_model=SuccessResponse)
def list_notifications(tipo: str = None, connection_id: str = None):
    from modules.webhook.schema import Notification
    
    try:
        if connection_id:
            notifications = Notification.find_by_connection_id(connection_id)
        else:
            notifications = Notification.find_all()
        
        if tipo:
            notifications = [n for n in notifications if n.tipo == tipo]
        
        notifications_data = [n.to_dict() for n in notifications]
        
        return JSONResponse(status_code=200, content=SuccessResponse(data=notifications_data).model_dump())
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(code="internal_error", data=f"Failed to retrieve notifications: {str(e)}").model_dump()
        )

@router.patch("/{notification_id}/read", response_model=SuccessResponse)
def update_notification_read_status(notification_id: str, request: UpdateReadStatusRequest = Body(...)):
    from modules.webhook.schema import Notification
    
    try:
        notification = Notification.find_by_id(notification_id)
        
        if not notification:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(code="not_found", data="Notification not found").model_dump()
            )
        
        notification.read = request.read
        notification.save()
        
        return JSONResponse(
            status_code=200,
            content=SuccessResponse(data=notification.to_dict()).model_dump()
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(code="internal_error", data=f"Failed to update notification: {str(e)}").model_dump()
        )