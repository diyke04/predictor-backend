from pydantic import BaseModel
from schemas.fixture import Fixture
from schemas.user import User

class PredictionCreate(BaseModel):
    fixture_id: int
    home_prediction_score:int
    away_prediction_score:int
    
class Prediction(BaseModel):
    id: int
    user: User
    fixture: Fixture
    home_prediction_score:int
    away_prediction_score:int
    
    class Config:
        from_attributes = True
