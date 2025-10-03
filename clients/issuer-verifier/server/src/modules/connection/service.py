from typing import List
from modules.utils.ssi import get_client
from modules.connection.schema import ConnectionResponse

async def get_connections(alias: str = None, state: str = None) -> List[dict] | str:
    try:
        result = await get_client().connection.get_connections(
            alias=alias,
            state=state
        )
        connections = result.to_dict() if hasattr(result, 'to_dict') else result
        if isinstance(connections, dict) and 'results' in connections:
            connections_list = []
            for conn in connections['results']:
                connections_list.append(
                    ConnectionResponse(
                        alias=conn.get('alias', ''),
                        connection_id=conn.get('connection_id', ''),
                        created_at=conn.get('created_at', ''),
                        invitation_key=conn.get('invitation_key', ''),
                        invitation_mode=conn.get('invitation_mode', ''),
                        state=conn.get('state', '')
                    )
                )
            return connections_list
        return []
    except Exception as e:
        return "CONNECTION_RETRIEVAL_FAILED"