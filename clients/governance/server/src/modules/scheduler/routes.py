from fastapi import APIRouter, HTTPException, status
from modules.utils.scheduler import voting_scheduler
from modules.utils.model import SuccessResponse

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

@router.get("/status", response_model=SuccessResponse[dict])
def get_scheduler_status():
    """
    Retorna o status do scheduler de votação
    """
    try:
        return SuccessResponse(data={
            "running": voting_scheduler.running,
            "check_interval": voting_scheduler.check_interval,
            "service": "Voting Scheduler"
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar status do scheduler"
        )

@router.post("/check-now", response_model=SuccessResponse[dict])
async def trigger_manual_check():
    """
    Força uma verificação manual das votações expiradas
    """
    try:
        await voting_scheduler.check_expired_votings()
        return SuccessResponse(data={
            "message": "Verificação manual executada com sucesso"
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar verificação manual: {str(e)}"
        )
