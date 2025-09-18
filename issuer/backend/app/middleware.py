"""
Middleware for handling SSI-related headers and authentication
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth import decode_access_token
from app.models.user import User
import jwt

class SSIHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically add user's public DID to request headers
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip middleware for non-authenticated routes
        if request.url.path in ["/docs", "/openapi.json", "/auth/login", "/auth/register", "/health"]:
            response = await call_next(request)
            return response
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                
                if payload:
                    user_id = payload.get("sub")
                    user = User.get_by_id(user_id)
                    
                    if user and hasattr(user, 'public_did') and user.public_did:
                        # Add public DID to request headers
                        request.headers.__dict__["_list"].append(
                            (b"x-public-did", user.public_did.encode())
                        )
                        
            except (jwt.InvalidTokenError, AttributeError) as e:
                # If token is invalid or user doesn't have public_did, continue without adding header
                pass
        
        response = await call_next(request)
        return response
