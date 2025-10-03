from modules.utils.headers import AuthHeaders
import modules.auth.service as auth_service
from modules.utils.model import ErrorResponse
from modules.auth.schema import AuthRegisterRequest, AuthLoginRequest, AuthResponse
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse)
async def register_user(credentials: AuthRegisterRequest):
    try:
        result = await auth_service.register_user(credentials)

        if result == "USER_ALREADY_EXISTS":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(code=result, data="Usuário já existe").model_dump()
            )
        if result == "DID_CREATION_FAILED":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(code=result, data="Falha na criação do DID").model_dump()
            )

        auth, headers = result
        return JSONResponse(status_code=201, content=AuthResponse(data=auth).model_dump(), headers=AuthHeaders(**headers).model_dump(by_alias=True))

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(code="INTERNAL_SERVER_ERROR", data=e.args[0] if e.args else "Erro ao registrar usuário").model_dump()
        )

@router.post("/login", response_model=AuthResponse)
def login_user(credentials: AuthLoginRequest):
    try:
        result = auth_service.login_user(credentials)

        if result == "USER_NOT_FOUND":
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(code=result, data="Usuário não encontrado").model_dump()
            )
        if result == "INVALID_PASSWORD":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse(code=result, data="Senha inválida").model_dump()
            )

        auth, headers = result
        return JSONResponse(status_code=200, content=AuthResponse(data=auth).model_dump(), headers=AuthHeaders(**headers).model_dump(by_alias=True))


    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(code="INTERNAL_SERVER_ERROR", data=e.args[0] if e.args else "Erro ao autenticar usuário").model_dump()
        )

    