from pydantic import BaseModel
from schemas.fixture import Fixture
from schemas.user import User

class PredictionCreate(BaseModel):
    fixture_id: int
    home_prediction_score:str
    away_prediction_score:str
    
class Prediction(BaseModel):
    id: int
    user: User
    fixture: Fixture
    home_prediction_score:str
    away_prediction_score:str
    result:str
    correct_score:str

  
class PredictionUpdate(BaseModel):
    home_prediction_score:str
    away_prediction_score:str
  
    
    class Config:
        from_attributes = True
