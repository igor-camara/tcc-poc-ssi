from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, Field

# TypeVar para permitir genéricos
T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """
    Estrutura base de resposta da API.
    """
    code: str = Field(..., description="Código de status personalizado da operação")
    data: Optional[T] = Field(None, description="Dados do resultado ou mensagem de erro")

# --------------------------
# Sucesso / Erro básicos
# --------------------------

class SuccessResponse(BaseResponse[T]):
    code: str = "SUCCESS"

class ErrorResponse(BaseResponse[str]):
    code: str = Field(..., description="Código de erro")
    data: str = Field(..., description="Mensagem de erro")

