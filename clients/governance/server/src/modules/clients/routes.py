from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from modules.clients.schema import ClientCreate, ClientResponse, ClientListResponse, ClientVotingResponse
from modules.clients.service import client_service
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("", response_model=SuccessResponse[ClientResponse], status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate):
    try:
        client = client_service.create_client(client_data)
        return SuccessResponse(data=client)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar cliente")

@router.get("", response_model=SuccessResponse[List[ClientListResponse]])
def get_clients(
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
    search: Optional[str] = Query(None)
):
    try:
        if search:
            clients = client_service.search_clients(search)
        elif status_filter:
            clients = client_service.get_clients_by_status(status_filter)
        elif type_filter:
            clients = client_service.get_clients_by_type(type_filter)
        else:
            clients = client_service.get_all_clients()
        
        return SuccessResponse(data=clients)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar clientes")

@router.get("/cnpj/{cnpj}", response_model=SuccessResponse[ClientResponse])
def get_client_by_cnpj(cnpj: str):
    try:
        if not cnpj.isdigit() or len(cnpj) != 14:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="CNPJ inválido. Deve conter exatamente 14 dígitos numéricos"
            )
        
        client = client_service.get_client_by_cnpj(cnpj)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return SuccessResponse(data=client)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar cliente")

@router.get("/{client_id}", response_model=SuccessResponse[ClientResponse])
def get_client(client_id: str):
    try:
        client = client_service.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return SuccessResponse(data=client)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar cliente")

@router.get("/{client_id}/votes", response_model=SuccessResponse[ClientVotingResponse])
def get_client_votes(client_id: str):
    try:
        voting_details = client_service.get_client_voting_details(client_id)
        if not voting_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return SuccessResponse(data=voting_details)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar votação do cliente")

@router.patch("/{client_id}/status", response_model=SuccessResponse[ClientResponse])
def update_client_status(client_id: str, new_status: str):
    try:
        client = client_service.update_client_status(client_id, new_status)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        return SuccessResponse(data=client)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar status do cliente")

@router.get("/statistics/overview", response_model=SuccessResponse[dict])
def get_statistics():
    try:
        stats = client_service.get_statistics()
        return SuccessResponse(data=stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar estatísticas")
