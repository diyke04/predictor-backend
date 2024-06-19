from core.config import RewardType
from sqlalchemy.orm import Session
from schemas.user import User
from schemas.prediction import Prediction
from fastapi import status

async def reward_user(user: User, reward_type: RewardType, db: Session):
    user.point += reward_type.value
    db.commit()

async def evaluate_prediction(prediction, db: Session):
    user = prediction.user
    if prediction.correct_score() == 'correct':
        await reward_user(user, RewardType.CORRECT_SCORE, db)
    
    if prediction.result() == prediction.fixture.result():
        await reward_user(user, RewardType.CORRECT_RESULT, db)
    
  