from core.config import RewardType
from sqlalchemy.orm import Session
from schemas.user import User
from schemas.prediction import Prediction
from fastapi import status

async def reward_user(user: User, reward_type: RewardType, db: Session):
    user.token += reward_type.value
    db.commit()

async def evaluate_prediction(prediction: Prediction, db: Session):
    user = prediction.user
    reward_user(user, RewardType.POST_PREDICTION, db)
    
    if prediction.correct_score() == 'correct':
        reward_user(user, RewardType.CORRECT_SCORE, db)
    
    if prediction.result() == prediction.fixture.result():
        reward_user(user, RewardType.CORRECT_RESULT, db)
    
    return {
        "status":status.HTTP_200_OK,
        "detail": "user reward updated"
    }