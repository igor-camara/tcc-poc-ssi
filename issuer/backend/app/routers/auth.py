"""
Authentication routes for FastAPI
"""
import asyncio
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    UserRegisterRequest, UserLoginRequest, AuthResponse, 
    UserResponse, SSIStatusResponse, ErrorResponse
)
from app.models.user import User
from app.auth import authenticate_user, create_access_token, get_current_user
from app.services.ssi_service import get_ssi_service

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """Register a new user"""
    try:
        existing_user = User.find_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já está em uso"
            )
        
        user = User(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        try:
            ssi_service = get_ssi_service()
            
            did_info = await ssi_service.create_and_register_did(user.email)
            
            user.did = did_info['did']
            user.verkey = did_info['verkey']
            user.did_metadata = {
                'alias': did_info.get('alias'),
                'registered_on_ledger': did_info.get('registered_on_ledger', False),
                'metadata': did_info.get('metadata', {})
            }
            
            print(f"Created DID {user.did} for user {user.email}")
            
        except Exception as e:
            print(f"Failed to create DID for user {user.email}: {str(e)}")
            print("Continuing registration without DID")
        
        user.save()
        
        access_token = create_access_token(data={"sub": user.id})
        
        return AuthResponse(
            token=access_token,
            user=UserResponse(**user.to_dict())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLoginRequest):
    """Authenticate user login"""
    try:
        user = authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Conta desativada"
            )
        
        access_token = create_access_token(data={"sub": user.id})
        
        return AuthResponse(
            token=access_token,
            user=UserResponse(**user.to_dict())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user.to_dict())

@router.get("/ssi-status", response_model=SSIStatusResponse)
async def get_ssi_status(current_user: User = Depends(get_current_user)):
    """Get SSI service status and user DID information"""
    try:
        try:
            ssi_service = get_ssi_service()
            
            status_info = SSIStatusResponse(
                ssi_service_available=True,
                acapy_url=ssi_service.controller.admin_url if ssi_service.controller else None,
                user_has_did=bool(current_user.did),
                user_did=current_user.did,
                user_verkey=current_user.verkey,
                did_metadata=current_user.did_metadata
            )
            
        except Exception as e:
            status_info = SSIStatusResponse(
                ssi_service_available=False,
                error=str(e),
                user_has_did=bool(current_user.did),
                user_did=current_user.did,
                user_verkey=current_user.verkey,
                did_metadata=current_user.did_metadata
            )
        
        return status_info
        
    except Exception as e:
        print(f"SSI status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )