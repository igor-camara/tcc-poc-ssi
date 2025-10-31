from typing import List, Optional
from modules.utils.mongodb import get_mongodb_client
from modules.utils.repositories import ClientRepository, VoteRepository, StewardRepository
from modules.clients.schema import ClientCreate, ClientResponse, ClientListResponse, ClientVotingResponse, ClientVoteDetail
from pymongo.errors import DuplicateKeyError
from datetime import timedelta

class ClientService:
    def __init__(self):
        self.db_client = get_mongodb_client()
        self.repository = ClientRepository(self.db_client)
        self.vote_repository = VoteRepository(self.db_client)
        self.steward_repository = StewardRepository(self.db_client)
    
    def _convert_to_response(self, client_data: dict) -> ClientResponse:
        client_data["id"] = str(client_data.pop("_id"))
        return ClientResponse(**client_data)
    
    def _convert_to_list_response(self, client_data: dict) -> ClientListResponse:
        client_data["id"] = str(client_data.pop("_id"))
        return ClientListResponse(**client_data)
    
    def create_client(self, client_data: ClientCreate) -> ClientResponse:
        existing_cnpj = self.repository.find_by_cnpj(client_data.cnpj)
        if existing_cnpj:
            raise ValueError("Cliente com este CNPJ já existe")
        
        existing_email = self.repository.find_by_email(client_data.email)
        if existing_email:
            raise ValueError("Cliente com este email já existe")
        
        try:
            client_id = self.repository.create_client(
                company_name=client_data.company_name,
                cnpj=client_data.cnpj,
                email=client_data.email,
                phone=client_data.phone,
                address=client_data.address,
                client_type=client_data.client_type,
                description=client_data.description,
                status="em_votacao"
            )
            
            created_client = self.repository.find_by_id(client_id)
            return self._convert_to_response(created_client)
        
        except DuplicateKeyError:
            raise ValueError("Cliente já existe no sistema")
    
    def get_client_by_id(self, client_id: str) -> Optional[ClientResponse]:
        client_data = self.repository.find_by_id(client_id)
        if not client_data:
            return None
        return self._convert_to_response(client_data)
    
    def get_client_by_cnpj(self, cnpj: str) -> Optional[ClientResponse]:
        client_data = self.repository.find_by_cnpj(cnpj)
        if not client_data:
            return None
        return self._convert_to_response(client_data)
    
    def get_all_clients(self) -> List[ClientListResponse]:
        clients = self.repository.find_all()
        return [self._convert_to_list_response(client) for client in clients]
    
    def get_clients_by_status(self, status: str) -> List[ClientListResponse]:
        clients = self.repository.find_by_status(status)
        return [self._convert_to_list_response(client) for client in clients]
    
    def get_clients_by_type(self, client_type: str) -> List[ClientListResponse]:
        clients = self.repository.find_by_type(client_type)
        return [self._convert_to_list_response(client) for client in clients]
    
    def search_clients(self, query: str) -> List[ClientListResponse]:
        clients = self.repository.search_clients(query)
        return [self._convert_to_list_response(client) for client in clients]
    
    def update_client_status(self, client_id: str, new_status: str) -> Optional[ClientResponse]:
        client = self.repository.find_by_id(client_id)
        if not client:
            return None
        
        self.repository.update_client_status(client_id, new_status)
        updated_client = self.repository.find_by_id(client_id)
        return self._convert_to_response(updated_client)
    
    def get_statistics(self) -> dict:
        return self.repository.get_client_statistics()
    
    def get_client_voting_details(self, client_id: str) -> Optional[ClientVotingResponse]:
        client = self.repository.find_by_id(client_id)
        if not client:
            return None
        
        # Buscar todos os votos do cliente
        votes = self.vote_repository.find_by_client(client_id)
        
        # Enriquecer votos com informações do steward
        vote_details = []
        for vote in votes:
            steward = self.steward_repository.find_by_id(str(vote["steward_id"]))
            vote_detail = ClientVoteDetail(
                id=str(vote["_id"]),
                steward_id=str(vote["steward_id"]),
                steward_name=steward["name"] if steward else "Desconhecido",
                vote=vote["vote"],
                comment=vote.get("comment"),
                created_at=vote["created_at"]
            )
            vote_details.append(vote_detail)
        
        # Contar votos
        vote_counts = self.vote_repository.count_votes_by_client(client_id)
        
        # Calcular deadline de votação
        first_vote_at = client.get("first_vote_at")
        voting_deadline = None
        if first_vote_at:
            voting_deadline = first_vote_at + timedelta(minutes=2)
        
        return ClientVotingResponse(
            client_id=str(client["_id"]),
            client_name=client["company_name"],
            status=client["status"],
            total_votes=vote_counts["total"],
            approve_votes=vote_counts["approve"],
            reject_votes=vote_counts["reject"],
            abstain_votes=vote_counts["abstain"],
            first_vote_at=first_vote_at,
            voting_deadline=voting_deadline,
            votes=vote_details
        )

client_service = ClientService()
