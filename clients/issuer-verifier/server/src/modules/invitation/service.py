from typing import Optional
from modules.utils.ssi import get_client

async def create_invitation(alias: Optional[str] = None, auto_accept: bool = True) -> dict | str:
    invitation_body = {}
    
    if alias:
        invitation_body["alias"] = alias
        invitation_body["my_label"] = "Invitation to " + alias
    
    if auto_accept:
        invitation_body["accept"] = ["didcomm/aip1", "didcomm/aip2;env=rfc19"]
    
    invitation_body["handshake_protocols"] = ["https://didcomm.org/didexchange/1.0"]

    result = await get_client().out_of_band.create_invitation(
        body=invitation_body
    )
    
    invitation_data = result.to_dict() if hasattr(result, 'to_dict') else result
    
    return invitation_data