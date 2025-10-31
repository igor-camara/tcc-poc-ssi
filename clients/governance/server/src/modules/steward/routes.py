from fastapi import APIRouter, HTTPException, status
from typing import List
from modules.steward.schema import StewardCreate, StewardResponse, StewardListResponse, VoteCreate, VoteResponse
from modules.steward.service import steward_service
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/stewards", tags=["stewards"])

@router.post("", response_model=SuccessResponse[StewardResponse], status_code=status.HTTP_201_CREATED)
def create_steward(steward_data: StewardCreate):
    try:
        steward = steward_service.create_steward(steward_data)
        return SuccessResponse(data=steward)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar steward")

@router.get("", response_model=SuccessResponse[List[StewardListResponse]])
def get_stewards(active_only: bool = False):
    try:
        if active_only:
            stewards = steward_service.get_active_stewards()
        else:
            stewards = steward_service.get_all_stewards()
        return SuccessResponse(data=stewards)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar stewards")

@router.get("/{steward_id}", response_model=SuccessResponse[StewardResponse])
def get_steward(steward_id: str):
    try:
        steward = steward_service.get_steward_by_id(steward_id)
        if not steward:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Steward não encontrado")
        return SuccessResponse(data=steward)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar steward")

@router.delete("/{steward_id}", status_code=status.HTTP_200_OK)
def delete_steward(steward_id: str):
    try:
        success = steward_service.delete_steward(steward_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Steward não encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar steward")

@router.get("/{steward_id}/votes", response_model=SuccessResponse[List[VoteResponse]])
def get_steward_votes(steward_id: str):
    try:
        votes = steward_service.get_steward_votes(steward_id)
        return SuccessResponse(data=votes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar votos do steward")

@router.post("/votes", response_model=SuccessResponse[VoteResponse], status_code=status.HTTP_201_CREATED)
def create_vote(vote_data: VoteCreate):
    try:
        vote = steward_service.create_vote(vote_data)
        return SuccessResponse(data=vote)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao registrar voto")
