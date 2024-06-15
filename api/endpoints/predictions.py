from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependency import get_current_user
from crud import crud_predictions, crud_fixtures
from schemas.prediction import PredictionCreate, Prediction
from db.session import get_db

router = APIRouter()

@router.post("/", response_model=Prediction)
def create_prediction(prediction: PredictionCreate, db: Session = Depends(get_db), user= Depends(get_current_user)):
    return crud_predictions.create_prediction(db=db, prediction=prediction, user_id=user.id)

@router.get("/user/{user_id}", response_model=List[Prediction])
def read_user_predictions(user_id: int, db: Session = Depends(get_db)):
    return crud_predictions.get_predictions_by_user(db=db, user_id=user_id)

@router.get("/fixture/{fixture_id}", response_model=List[Prediction])
def read_fixture_predictions(fixture_id: int, db: Session = Depends(get_db)):
    return crud_predictions.get_predictions_by_fixture(db=db, fixture_id=fixture_id)

@router.get("/results/{user_id}", response_model=List[Prediction])
def read_user_prediction_results(user_id: int, db: Session = Depends(get_db)):
    user_predictions = crud_predictions.get_predictions_by_user(db=db, user_id=user_id)
    results = []
    for prediction in user_predictions:
        fixture = crud_fixtures.get_fixture(db=db, fixture_id=prediction.fixture_id)
        if fixture.home_team_score is not None and fixture.away_team_score is not None:
            # Here you can compare the prediction with the actual result
            # and append to the results list
            if (fixture.home_team_score > fixture.away_team_score and prediction.prediction == "home") or \
               (fixture.home_team_score < fixture.away_team_score and prediction.prediction == "away") or \
               (fixture.home_team_score == fixture.away_team_score and prediction.prediction == "draw"):
                results.append({"fixture_id": fixture.id, "prediction": prediction.prediction, "result": "correct"})
            else:
                results.append({"fixture_id": fixture.id, "prediction": prediction.prediction, "result": "incorrect"})
    return results
