from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from modules.auth.schema import LoginRequest, LoginResponse, TOTPSetupResponse
from modules.auth.service import AuthService
import os

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Endpoint de autenticação com TOTP
    
    Usuário mockado:
    - username: igor.admin
    - Use o Google Authenticator configurado via QR code do endpoint /auth/setup
    """
    # Verificar se o usuário existe
    if request.username != AuthService.MOCK_USER["username"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    # Verificar código TOTP
    if not AuthService.verify_totp(request.username, request.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código TOTP inválido"
        )
    
    return LoginResponse(
        success=True,
        message="Login realizado com sucesso",
        username=request.username
    )


@router.get("/setup/{username}", response_model=TOTPSetupResponse)
async def setup_totp(username: str) -> TOTPSetupResponse:
    """
    Gera QR code para configuração do Google Authenticator
    
    Use este endpoint para obter o QR code e configurar o Google Authenticator.
    Usuário disponível: igor.admin
    """
    try:
        setup_data = AuthService.generate_qr_code(username)
        return TOTPSetupResponse(**setup_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/setup-page", response_class=HTMLResponse)
async def setup_page():
    """
    Página HTML para configuração do Google Authenticator
    
    Acesse esta página no navegador para ver o QR code e instruções de configuração.
    """
    html_path = os.path.join(os.path.dirname(__file__), "setup.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

