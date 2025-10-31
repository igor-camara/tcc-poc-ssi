from typing import List, Optional
from modules.utils.mongodb import get_mongodb_client
from modules.utils.repositories import StewardRepository, VoteRepository, ClientRepository
from modules.steward.schema import StewardCreate, StewardResponse, StewardListResponse, VoteCreate, VoteResponse
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from datetime import datetime, timedelta

MOCK_STEWARDS = [
    {
        "name": "Dr. Carlos Silva",
        "email": "carlos.silva@governance.com",
        "organization": "Governança Digital Brasil",
        "role": "steward"
    },
    {
        "name": "Dra. Maria Santos",
        "email": "maria.santos@governance.com",
        "organization": "Governança Digital Brasil",
        "role": "steward"
    },
    {
        "name": "Prof. João Oliveira",
        "email": "joao.oliveira@university.edu.br",
        "organization": "Universidade Federal Tech",
        "role": "steward"
    },
    {
        "name": "Ana Costa",
        "email": "ana.costa@certifica.org",
        "organization": "Instituto Certificador Nacional",
        "role": "steward"
    },
    {
        "name": "Ricardo Mendes",
        "email": "ricardo.mendes@blockchain.org",
        "organization": "Blockchain Association",
        "role": "steward"
    }
]

class StewardService:
    def __init__(self):
        self.db_client = get_mongodb_client()
        self.repository = StewardRepository(self.db_client)
        self.vote_repository = VoteRepository(self.db_client)
        self.client_repository = ClientRepository(self.db_client)
        self._initialize_stewards()
    
    def _initialize_stewards(self):
        existing_count = self.repository.count()
        if existing_count == 0:
            for steward_data in MOCK_STEWARDS:
                try:
                    self.repository.create_steward(**steward_data)
                except DuplicateKeyError:
                    pass
    
    def _convert_to_response(self, steward_data: dict) -> StewardResponse:
        steward_data["id"] = str(steward_data.pop("_id"))
        return StewardResponse(**steward_data)
    
    def _convert_to_list_response(self, steward_data: dict) -> StewardListResponse:
        steward_data["id"] = str(steward_data.pop("_id"))
        return StewardListResponse(**steward_data)
    
    def _convert_vote_to_response(self, vote_data: dict) -> VoteResponse:
        vote_data["id"] = str(vote_data.pop("_id"))
        vote_data["steward_id"] = str(vote_data["steward_id"])
        vote_data["client_id"] = str(vote_data["client_id"])
        return VoteResponse(**vote_data)
    
    def create_steward(self, steward_data: StewardCreate) -> StewardResponse:
        existing_email = self.repository.find_by_email(steward_data.email)
        if existing_email:
            raise ValueError("Steward com este email já existe")
        
        try:
            steward_id = self.repository.create_steward(
                name=steward_data.name,
                email=steward_data.email,
                organization=steward_data.organization,
                role=steward_data.role
            )
            
            created_steward = self.repository.find_by_id(steward_id)
            return self._convert_to_response(created_steward)
        
        except DuplicateKeyError:
            raise ValueError("Steward já existe no sistema")
    
    def get_steward_by_id(self, steward_id: str) -> Optional[StewardResponse]:
        steward_data = self.repository.find_by_id(steward_id)
        if not steward_data:
            return None
        return self._convert_to_response(steward_data)
    
    def get_all_stewards(self) -> List[StewardListResponse]:
        stewards = self.repository.find_all()
        return [self._convert_to_list_response(s) for s in stewards]
    
    def get_active_stewards(self) -> List[StewardListResponse]:
        stewards = self.repository.find_active_stewards()
        return [self._convert_to_list_response(s) for s in stewards]
    
    def delete_steward(self, steward_id: str) -> bool:
        return self.repository.delete_by_id(steward_id)
    
    def get_steward_votes(self, steward_id: str) -> List[VoteResponse]:
        steward = self.repository.find_by_id(steward_id)
        if not steward:
            raise ValueError("Steward não encontrado")
        
        votes = self.vote_repository.find_by_steward(steward_id)
        return [self._convert_vote_to_response(vote) for vote in votes]
    
    def create_vote(self, vote_data: VoteCreate) -> VoteResponse:
        steward = self.repository.find_by_id(vote_data.steward_id)
        if not steward:
            raise ValueError("Steward não encontrado")
        
        client = self.client_repository.find_by_id(vote_data.client_id)
        if not client:
            raise ValueError("Cliente não encontrado")
        
        # Verificar se o cliente ainda está em votação
        if client.get("status") != "em_votacao":
            raise ValueError("Cliente não está mais em processo de votação")
        
        existing_vote = self.vote_repository.find_vote(vote_data.steward_id, vote_data.client_id)
        if existing_vote:
            raise ValueError("Steward já votou neste cliente")
        
        try:
            # Registrar o timestamp do primeiro voto
            if not client.get("first_vote_at"):
                self.client_repository.set_first_vote_timestamp(vote_data.client_id)
                client = self.client_repository.find_by_id(vote_data.client_id)
            
            vote_id = self.vote_repository.create_vote(
                steward_id=vote_data.steward_id,
                client_id=vote_data.client_id,
                vote=vote_data.vote,
                comment=vote_data.comment
            )
            
            # Verificar condições de finalização da votação
            vote_counts = self.vote_repository.count_votes_by_client(vote_data.client_id)
            total_stewards = self.repository.count({"status": "active"})
            
            # Verificar se o tempo de votação expirou (2 minutos após o primeiro voto)
            first_vote_at = client.get("first_vote_at")
            voting_expired = False
            if first_vote_at:
                deadline = first_vote_at + timedelta(minutes=2)
                voting_expired = datetime.utcnow() > deadline
            
            # Verificar se todos os stewards votaram
            all_voted = vote_counts["total"] >= total_stewards
            
            # Verificar se pelo menos 50% dos stewards participaram
            min_participation = total_stewards * 0.5
            has_min_participation = vote_counts["total"] >= min_participation
            
            # Finalizar votação se: todos votaram OU tempo expirou com participação mínima
            should_finalize = all_voted or (voting_expired and has_min_participation)
            
            if should_finalize:
                # Calcular resultado
                # Para aprovação: pelo menos 2/3 dos votos válidos (approve + reject) devem ser approve
                valid_votes = vote_counts["approve"] + vote_counts["reject"]
                required_approvals = valid_votes * (2/3)
                
                if vote_counts["approve"] >= required_approvals and has_min_participation:
                    # Aprovar cliente
                    self.client_repository.update_client_status(vote_data.client_id, "aprovado")
                    # Gerar e definir a chave de API para o cliente aprovado
                    api_key = self.client_repository.generate_api_key()
                    self.client_repository.set_api_key(vote_data.client_id, api_key)
                else:
                    self.client_repository.update_client_status(vote_data.client_id, "rejeitado")
            
            created_vote = self.vote_repository.find_by_id(vote_id)
            return self._convert_vote_to_response(created_vote)
        
        except DuplicateKeyError:
            raise ValueError("Voto já registrado")

steward_service = StewardService()
