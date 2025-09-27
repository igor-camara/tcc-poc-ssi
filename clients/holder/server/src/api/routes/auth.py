from api.schemas.request import AuthRegisterRequest, AuthLoginRequest
from api.schemas.response import AuthResponse
from api.schemas.headers import AuthHeaders
from api.service.agent import create_did, register_did_on_ledger
from api.service.user import create_user, get_user_by_email
from api.utils.token import create_access_token
from api.utils.password import verify_password
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
async def register_user(credentials: AuthRegisterRequest):
    try:

        existing_user = get_user_by_email(credentials.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário com este email já existe"
            )

        did_info = await create_did(credentials.email)

        is_registered = await register_did_on_ledger(did_info['did'], did_info['verkey'], did_info['alias'])

        if not is_registered:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao registrar DID na ledger"
            )
        
        user = create_user(
            name=credentials.full_name,
            email=credentials.email,
            password=credentials.password,
            did=did_info['did'],
            verkey=did_info['verkey']
        )

        access_token = create_access_token(data={"sub": user.id})

        response = AuthResponse(
            user_name=user.first_name,
            user_surname=user.last_name,
            user_email=user.email
        )

        auth_headers = AuthHeaders(
            token=access_token,
            did=user.did,
            verkey=user.verkey
        )

        return JSONResponse(status_code=201, content=response.model_dump(), headers=auth_headers.model_dump())

    except Exception as e:
        raise Exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        ) from e

@router.post("/login", response_model=AuthResponse)
def login_user(credentials: AuthLoginRequest):

    user = get_user_by_email(credentials.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )
    
    access_token = create_access_token(data={"sub": user.id})

    response = AuthResponse(
        user_name=user.first_name,
        user_surname=user.last_name,
        user_email=user.email
    )

    auth_headers = AuthHeaders(
        token=access_token,
        did=user.did,
        verkey=user.verkey
    )

    return JSONResponse(status_code=200, content=response.model_dump(), headers=auth_headers.model_dump())