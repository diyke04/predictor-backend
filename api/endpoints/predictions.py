from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependency import get_current_user
from crud import crud_predictions, crud_fixtures
from schemas.prediction import PredictionCreate, Prediction,PredictionUpdate
from db.session import get_db

router = APIRouter()

@router.post("/", response_model=Prediction)
async def create_prediction(prediction: PredictionCreate, db: Session = Depends(get_db), user= Depends(get_current_user)):
    return await crud_predictions.create_prediction(db=db, prediction=prediction, user_id=user.id)

@router.get("/user", response_model=List[Prediction])
async def get_user_predictions(user_id: int, db: Session = Depends(get_db)):
    return await crud_predictions.get_predictions_by_user(db=db, user_id=user_id)

@router.get("/fixture", response_model=List[Prediction])
async def get_predictions_on_fixture(fixture_id: int, db: Session = Depends(get_db)):
    return await crud_predictions.get_predictions_by_fixture(db=db, fixture_id=fixture_id)

@router.get("/user/league", response_model=List[Prediction])
async def get_predictions_in_league(league_id: int,user_id:int, db: Session = Depends(get_db)):
    return await crud_predictions.get_user_predictions_in_league(db=db, league_id=league_id,user_id=user_id)

@router.put('/update',response_model=Prediction)
async def update_prediction(prediction_id:int,scores:PredictionUpdate ,user=Depends(get_current_user),db=Depends(get_db)):
    return await crud_predictions.update_user_prediction(user_id=user.id,prediction_id=prediction_id,score=scores,db=db)

@router.delete('/delete')
async def delete_prediction(prediction_id:int,user=Depends(get_current_user),db=Depends(get_db)):
    return await crud_predictions.delete_user_prediction(user_id=user.id,prediction_id=prediction_id,db=db)
