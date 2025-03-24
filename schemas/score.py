from pydantic import BaseModel

class Score(BaseModel):
    node_id: str
    score: int