import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from modules.client.service import AcaPyClient
from modules.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class ProofRequestScheduler:
    """Scheduler para invalidar pedidos de prova pendentes"""
    
    def __init__(self):
        self.task: Optional[asyncio.Task] = None
        self.running = False
        
    async def invalidate_pending_proofs(self):
        """Verifica e invalida pedidos de prova que estão pendentes há muito tempo"""
        try:
            logging.info("Verificando pedidos de prova pendentes...")
            
            # Busca todas as provas
            proofs = AcaPyClient.verify.get_all_proofs(
                descending=True,
                limit=100,
                offset=0
            )
            
            if not proofs:
                logging.info("Nenhuma prova encontrada.")
                return
            
            # Estados que indicam que a prova está pendente de resposta do holder
            pending_states = ["request-sent", "request-received"]
            now = datetime.now(timezone.utc)
            invalidated_count = 0
            
            for proof in proofs:
                state = proof.get("state")
                pres_ex_id = proof.get("pres_ex_id")
                updated_at = proof.get("updated_at")
                role = proof.get("role")
                
                # Apenas processa provas onde somos o verifier (quem solicitou)
                if role != "verifier":
                    continue
                
                # Verifica se está em estado pendente
                if state not in pending_states:
                    continue
                
                # Calcula tempo desde a última atualização
                if updated_at:
                    try:
                        # Parse do timestamp (formato: "2024-12-08T12:34:56.789Z")
                        updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        time_elapsed = (now - updated_time).total_seconds()
                        
                        # Se passou mais tempo que o timeout configurado, invalida
                        if time_elapsed > settings.proof_request_timeout:
                            logging.info(
                                f"Invalidando prova {pres_ex_id} - "
                                f"Estado: {state}, Tempo decorrido: {time_elapsed:.0f}s"
                            )
                            
                            result = AcaPyClient.verify.send_problem_report(
                                pres_ex_id=pres_ex_id,
                                description="Proof request timed out due to no response from holder"
                            )
                            
                            if result:
                                invalidated_count += 1
                                logging.info(f"Prova {pres_ex_id} invalidada com sucesso.")
                            else:
                                logging.warning(f"Falha ao invalidar prova {pres_ex_id}.")
                    except (ValueError, TypeError) as e:
                        logging.error(f"Erro ao processar timestamp da prova {pres_ex_id}: {e}")
                        continue
            
            if invalidated_count > 0:
                logging.info(f"Total de provas invalidadas: {invalidated_count}")
            else:
                logging.info("Nenhuma prova pendente para invalidar.")
                
        except Exception as e:
            logging.exception(f"Erro ao invalidar provas pendentes: {e}")
    
    async def run(self):
        """Executa o scheduler periodicamente"""
        self.running = True
        logging.info(
            f"Scheduler iniciado - Verificando a cada {settings.proof_check_interval}s, "
            f"timeout de {settings.proof_request_timeout}s"
        )
        
        while self.running:
            try:
                await self.invalidate_pending_proofs()
                await asyncio.sleep(settings.proof_check_interval)
            except asyncio.CancelledError:
                logging.info("Scheduler cancelado.")
                break
            except Exception as e:
                logging.exception(f"Erro no loop do scheduler: {e}")
                await asyncio.sleep(settings.proof_check_interval)
    
    def start(self):
        """Inicia o scheduler em background"""
        if not settings.enable_proof_scheduler:
            logging.info("Scheduler de invalidação de provas desabilitado.")
            return
        
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run())
            logging.info("Task do scheduler criada.")
    
    async def stop(self):
        """Para o scheduler"""
        self.running = False
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            logging.info("Scheduler parado.")

# Instância global do scheduler
proof_scheduler = ProofRequestScheduler()

def start_scheduler():
    """Função helper para iniciar o scheduler"""
    proof_scheduler.start()

async def stop_scheduler():
    """Função helper para parar o scheduler"""
    await proof_scheduler.stop()
