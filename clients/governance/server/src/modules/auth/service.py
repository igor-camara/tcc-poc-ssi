import pyotp
import qrcode
import io
import base64
from typing import Dict


class AuthService:
    """Serviço de autenticação com TOTP"""
    
    # Usuário mockado
    MOCK_USER = {
        "username": "igor.admin",
        "totp_secret": "JBSWY3DPEHPK3PXP"  # Secret fixo para o usuário mockado
    }
    
    @staticmethod
    def get_user_totp_secret(username: str) -> str | None:
        """Obtém o secret TOTP do usuário"""
        if username == AuthService.MOCK_USER["username"]:
            return AuthService.MOCK_USER["totp_secret"]
        return None
    
    @staticmethod
    def verify_totp(username: str, totp_code: str) -> bool:
        """Verifica o código TOTP fornecido"""
        secret = AuthService.get_user_totp_secret(username)
        if not secret:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(totp_code, valid_window=1)  # valid_window=1 aceita códigos 30s antes/depois
    
    @staticmethod
    def generate_qr_code(username: str) -> Dict[str, str]:
        """Gera QR code e informações para configuração do TOTP"""
        secret = AuthService.get_user_totp_secret(username)
        if not secret:
            raise ValueError(f"Usuário {username} não encontrado")
        
        # Criar URI de provisionamento
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name="Governance Server SSI"
        )
        
        # Gerar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Converter QR code para base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        qr_code_data_url = f"data:image/png;base64,{img_str}"
        
        return {
            "username": username,
            "secret": secret,
            "qr_code_url": qr_code_data_url,
            "provisioning_uri": provisioning_uri
        }
