from fastapi import APIRouter, HTTPException, status, Header, Query
from typing import Optional
from modules.schemas.schemas import SchemaCreate, SchemaResponse, SchemaListResponse
from modules.schemas.service import schema_service
from modules.utils.model import SuccessResponse
from modules.utils.repositories import ClientRepository
from modules.utils.mongodb import get_mongodb_client

router = APIRouter(prefix="/schemas", tags=["schemas"])


def validate_api_key_basic(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Valida apenas se a API key é válida e o cliente está aprovado
    
    Args:
        x_api_key: API key do header
        
    Returns:
        client_id do cliente autenticado
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header é obrigatório"
        )
    
    db_client = get_mongodb_client()
    client_repository = ClientRepository(db_client)
    
    client = client_repository.find_one({"api_key": x_api_key})
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    
    if client.get("status") != "aprovado":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente não está aprovado"
        )
    
    return str(client["_id"])


def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Valida a API key e verifica se o cliente pode registrar schemas
    
    Args:
        x_api_key: API key do header
        
    Returns:
        client_id do cliente autenticado
    """
    client_id = validate_api_key_basic(x_api_key)
    
    db_client = get_mongodb_client()
    client_repository = ClientRepository(db_client)
    client = client_repository.find_by_id(client_id)
    
    # Valida se o cliente é issuer ou both
    client_type = client.get("client_type")
    if client_type not in ["issuer", "both"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes do tipo issuer ou both podem registrar schemas"
        )
    
    return client_id


@router.post("", response_model=SuccessResponse[SchemaResponse], status_code=status.HTTP_201_CREATED)
def register_schema(
    schema_data: SchemaCreate,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Registra um schema criado por um issuer válido
    
    Args:
        schema_data: Dados do schema (schema_id)
        x_api_key: API key do issuer
        
    Returns:
        Schema registrado com sucesso
    """
    try:
        client_id = validate_api_key(x_api_key)
        
        schema = schema_service.register_schema(client_id, schema_data.schema_id)
        
        return SuccessResponse(data=schema)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar schema: {str(e)}"
        )


@router.get("", response_model=SuccessResponse[SchemaListResponse])
def list_schemas(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página"),
    search: Optional[str] = Query(None, description="Busca por nome do emissor ou credencial"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Lista schemas com paginação e busca
    
    Args:
        page: Número da página (inicia em 1)
        page_size: Quantidade de itens por página (1-100)
        search: Termo de busca para filtrar por nome do emissor ou credencial
        x_api_key: API key do usuário autenticado
        
    Returns:
        Lista paginada de schemas com informações detalhadas
    """
    try:
        # Valida a API key (apenas verifica se o usuário é válido e aprovado)
        validate_api_key_basic(x_api_key)
        
        # Busca schemas
        result = schema_service.get_schemas(page, page_size, search)
        
        return SuccessResponse(data=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar schemas: {str(e)}"
        )
