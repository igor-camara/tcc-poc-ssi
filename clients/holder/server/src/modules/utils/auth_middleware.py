"""
Middleware para validação de JWT tokens nas requisições autenticadas
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from modules.config.settings import settings
import modules.user.service as user_service

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para extrair e validar o usuário atual do JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        did: Optional[str] = payload.get("did")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Dependency para verificar se o usuário está ativo
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def verify_did_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> tuple:
    """
    Dependency específica para tokens DID que retorna (user, did)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate DID credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        did: str = payload.get("did")
        
        if user_id is None or did is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_id(user_id)
    if user is None or user.did != did:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user, did