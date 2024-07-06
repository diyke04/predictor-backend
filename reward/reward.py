from core.config import RewardType
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import User

async def reward_user(user: User, reward_type: RewardType, db: AsyncSession):
    user.point += reward_type.value
    await db.commit()

async def evaluate_prediction(prediction, db: AsyncSession):
    user = prediction.user
    if prediction.correct_score() == 'correct':
        await reward_user(user, RewardType.CORRECT_SCORE, db)
    
    if prediction.result() == prediction.fixture.result():
        await reward_user(user, RewardType.CORRECT_RESULT, db)
    
  