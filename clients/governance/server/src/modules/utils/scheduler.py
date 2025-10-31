import asyncio
from datetime import datetime, timedelta
from typing import Optional
from modules.utils.mongodb import get_mongodb_client
from modules.utils.repositories import ClientRepository, VoteRepository, StewardRepository
import logging

logger = logging.getLogger(__name__)

class VotingScheduler:
    def __init__(self, check_interval: int = 10):
        self.check_interval = check_interval
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        # Inicializar repositórios
        self.db_client = get_mongodb_client()
        self.client_repository = ClientRepository(self.db_client)
        self.vote_repository = VoteRepository(self.db_client)
        self.steward_repository = StewardRepository(self.db_client)
    
    async def check_expired_votings(self):
        try:
            # Buscar todos os clientes em votação
            clients_in_voting = self.client_repository.find_by_status("em_votacao")
            
            now = datetime.utcnow()
            
            for client in clients_in_voting:
                first_vote_at = client.get("first_vote_at")
                
                # Se ainda não teve primeiro voto, pular
                if not first_vote_at:
                    continue
                
                # Calcular deadline (2 minutos após primeiro voto)
                deadline = first_vote_at + timedelta(minutes=2)
                
                # Se o prazo expirou
                if now > deadline:
                    client_id = str(client["_id"])
                    await self._finalize_voting(client_id, client)
        
        except Exception as e:
            logger.error(f"Erro ao verificar votações expiradas: {e}")
    
    async def _finalize_voting(self, client_id: str, client: dict):
        try:
            vote_counts = self.vote_repository.count_votes_by_client(client_id)
            total_stewards = self.steward_repository.count({"status": "active"})
            
            # Verificar participação mínima (50%)
            min_participation = total_stewards * 0.5
            has_min_participation = vote_counts["total"] >= min_participation
            
            if not has_min_participation:
                # Participação insuficiente - rejeitar
                self.client_repository.update_client_status(client_id, "rejeitado")
                logger.info(
                    f"Cliente {client_id} ({client.get('company_name')}) rejeitado: "
                    f"participação insuficiente ({vote_counts['total']}/{total_stewards})"
                )
                return
            
            # Calcular resultado baseado em 2/3 dos votos válidos
            valid_votes = vote_counts["approve"] + vote_counts["reject"]
            
            if valid_votes == 0:
                # Apenas abstenções - rejeitar
                self.client_repository.update_client_status(client_id, "rejeitado")
                logger.info(
                    f"Cliente {client_id} ({client.get('company_name')}) rejeitado: "
                    f"apenas votos de abstenção"
                )
                return
            
            required_approvals = valid_votes * (2/3)
            
            if vote_counts["approve"] >= required_approvals:
                self.client_repository.update_client_status(client_id, "aprovado")
                logger.info(
                    f"Cliente {client_id} ({client.get('company_name')}) aprovado: "
                    f"{vote_counts['approve']}/{valid_votes} votos favoráveis "
                    f"(necessário: {required_approvals:.1f})"
                )
            else:
                self.client_repository.update_client_status(client_id, "rejeitado")
                logger.info(
                    f"Cliente {client_id} ({client.get('company_name')}) rejeitado: "
                    f"{vote_counts['approve']}/{valid_votes} votos favoráveis "
                    f"(necessário: {required_approvals:.1f})"
                )
        
        except Exception as e:
            logger.error(f"Erro ao finalizar votação do cliente {client_id}: {e}")
    
    async def run(self):
        self.running = True
        logger.info(f"Voting Scheduler iniciado (intervalo: {self.check_interval}s)")
        
        while self.running:
            try:
                await self.check_expired_votings()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Erro no loop do scheduler: {e}")
                await asyncio.sleep(self.check_interval)
    
    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self.run())
            logger.info("Voting Scheduler task criada")
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            logger.info("Voting Scheduler parado")

voting_scheduler = VotingScheduler(check_interval=10)
