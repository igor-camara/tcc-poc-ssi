from modules.client.service import AcaPyClient
from modules.user.schema import User

def create_did(alias: str = None) -> dict | str:
    try:
        result = AcaPyClient.did.create()
        
        return {
            'did': result.get('did'),
            'verkey': result.get('verkey'),
            'alias': alias
        }
    except Exception as e:
        print(e)
        return "DID_CREATION_FAILED"

def receive(alias: str, invitation_url: dict, user_did: str) -> dict | str:
    try:
        result = AcaPyClient.connection.receive(alias, invitation_url)

        conn = AcaPyClient.connection.get_connections(invitation_msg_id=result.get("@id"))

        my_did = conn.get("my_did")

        User.add_ephemeral_did(user_did, my_did)
    except Exception as e:
        print(e)
        return "INVITATION_RECEIVE_FAILED"
