from modules.client.schemas import ClientDid, ClientConnection, ClientSchemas, ClientIssue, ClientVerify
from modules.config.settings import settings

class ClientService:
    def __init__(self, url: str):
        self.did = ClientDid(url)
        self.connection = ClientConnection(url)
        self.schemas = ClientSchemas(url)
        self.issue = ClientIssue(url)
        self.verify = ClientVerify(url)

AcaPyClient = ClientService(settings.admin_url)