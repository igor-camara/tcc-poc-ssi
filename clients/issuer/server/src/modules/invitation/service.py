from modules.client.service import AcaPyClient
from modules.config.settings import settings

def create_invitation(alias: str) -> dict | str:
    public_did = AcaPyClient.did.get_public_did()

    if not public_did:
        return "NO_PUBLIC_DID_FOUND"

    return AcaPyClient.connection.create(alias, settings.company_name, public_did=public_did['did'])