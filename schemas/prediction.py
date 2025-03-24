from pydantic import BaseModel

class Prediction(BaseModel):
    node_id: str
    prediction: int