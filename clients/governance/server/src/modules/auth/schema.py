from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    username: str = Field(..., description="Nome de usuário")
    totp_code: str = Field(..., description="Código TOTP de 6 dígitos", min_length=6, max_length=6)


class LoginResponse(BaseModel):
    """Schema para resposta de login"""
    success: bool
    message: str
    username: str | None = None


class TOTPSetupResponse(BaseModel):
    """Schema para resposta de configuração do TOTP"""
    username: str
    secret: str
    qr_code_url: str
    provisioning_uri: str
