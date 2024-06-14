from pydantic import BaseModel

class PredictionCreate(BaseModel):
    fixture_id: int
    prediction: str

class Prediction(BaseModel):
    id: int
    user_id: int
    fixture_id: int
    prediction: str
    
    class Config:
        from_attributes = True
