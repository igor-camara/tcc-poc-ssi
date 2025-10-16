from modules.client.service import AcaPyClient

def create_invitation(alias: str) -> dict | str:
    public_did = AcaPyClient.did.get_public_did()

    if not public_did:
        return "NO_PUBLIC_DID_FOUND"

    return AcaPyClient.connection.create(alias, f"Convite de conexão para {alias}", public_did=public_did['did'])