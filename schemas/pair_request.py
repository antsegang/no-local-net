from pydantic import BaseModel

class PairRequest(BaseModel):
    remote_peer_id: str