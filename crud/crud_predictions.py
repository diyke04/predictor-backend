from sqlalchemy.orm import Session
from models.prediction import Prediction
from models.fixture import Fixture
from models.league import League
from schemas.prediction import PredictionCreate,PredictionUpdate
from fastapi import HTTPException, status
from reward import reward
from core.config import RewardType

async def create_prediction(db: Session, prediction: PredictionCreate, user_id: int):
    db_prediction = Prediction(**prediction.model_dump(), user_id=user_id)
    db.add(db_prediction)
    await db.commit()
    await db.refresh(db_prediction)
    await reward.reward_user(user=db_prediction.user,db=db,reward_type=RewardType.POST_PREDICTION)
    return db_prediction.to_dict()

async def get_predictions_by_user(db: Session, user_id: int):
    predictions=db.query(Prediction).filter(Prediction.user_id == user_id).all()
    prediction_response=[
        prediction.to_dict()
        for  prediction in predictions
    ]
    return prediction_response

async def get_predictions_by_fixture(db: Session, fixture_id: int):
    fixture_predictions= db.query(Prediction).filter(Prediction.fixture_id == fixture_id).all()
    fixture_response = [
        prediction.to_dict()
        for prediction in fixture_predictions
    ]
    return fixture_response

async def get_user_predictions_in_league(db: Session, user_id: int, league: str):
    predictions = db.query(Prediction).join(Fixture).filter(
        Prediction.user_id == user_id,
        Fixture.league == league
    ).all()

    predictions_response=[
        prediction.to_dict() for prediction in predictions
    ]

    return predictions_response

async def update_user_prediction(db:Session,user_id:int,prediction_id:int,score:PredictionUpdate):

    prediction_obj =db.query(Prediction).filter(Prediction.user_id==user_id,Prediction.id==prediction_id).first()
    if not prediction_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    prediction_obj.home_prediction_score=score.home_prediction_score
    prediction_obj.away_prediction_score=score.away_prediction_score

    db.add(prediction_obj)
    await db.commit()
    await db.refresh(prediction_obj)

    return prediction_obj.to_dict()

async def delete_user_prediction(db:Session,user_id:int,prediction_id):
    prediction_obj =db.query(Prediction).filter(Prediction.user_id==user_id,Prediction.id==prediction_id).first()

    if not prediction_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if prediction_obj.fixture.status.value=='completed'or prediction_obj.fixture.status.value =='in_progress':
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="Match already Ended")


    db.delete(prediction_obj)
    await db.commit()
    
    await reward.reward_user(user=prediction_obj.user,reward_type=RewardType.DELETE_PREDICTION,db=db)

    return {"status":status.HTTP_200_OK,"detail":"prediction deleted"}


