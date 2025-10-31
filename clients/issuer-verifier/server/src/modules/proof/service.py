
from modules.client.service import AcaPyClient

def create_proof_request(payload: dict) -> dict | str:
    proof_req = payload.get("proof_request", {})
    connection_id = payload.get("connection_id")
    if not connection_id or not proof_req:
        return {"error": "connection_id and proof_request are required"}

    requested_attributes = {}
    for referent, attr in proof_req.get("requested_attributes", {}).items():
        attr_payload = {}
        if "name" in attr:
            attr_payload["name"] = attr["name"]
        if "names" in attr:
            attr_payload["names"] = attr["names"]
        if "restrictions" in attr:
            attr_payload["restrictions"] = attr["restrictions"]
        requested_attributes[referent] = attr_payload

    requested_predicates = {}
    for referent, pred in proof_req.get("requested_predicates", {}).items():
        pred_payload = {}
        for k in ["name", "p_type", "p_value", "restrictions"]:
            if k in pred:
                pred_payload[k] = pred[k]
        requested_predicates[referent] = pred_payload

    props = {
        "connection_id": connection_id,
        "schema_name": proof_req.get("name", "Proof Request"),
        "version": proof_req.get("version", "1.0"),
        "requested_attributes": requested_attributes,
        "requested_predicates": requested_predicates,
        "auto_remove": False
    }

    result = AcaPyClient.verify.send_proof_request(props)
    return result

def get_all_proofs(descending: bool = False, limit: int = 100, offset: int = 0):
    result = AcaPyClient.verify.get_all_proofs(descending=descending, limit=limit, offset=offset)
    return result

def get_proof_by_id(pres_ex_id: str):
    result = AcaPyClient.verify.get_proof_by_id(pres_ex_id)
    return result