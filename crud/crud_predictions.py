from sqlalchemy.orm import Session
from models.prediction import Prediction
from models.fixture import Fixture
from models.league import League
from schemas.prediction import PredictionCreate

def create_prediction(db: Session, prediction: PredictionCreate, user_id: int):
    db_prediction = Prediction(**prediction.dict(), user_id=user_id)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_predictions_by_user(db: Session, user_id: int):
    return db.query(Prediction).filter(Prediction.user_id == user_id).all()

def get_predictions_by_fixture(db: Session, fixture_id: int):
    return db.query(Prediction).filter(Prediction.fixture_id == fixture_id).all()

def get_user_predictions_in_league(db: Session, user_id: int, league_id: int):
    predictions = db.query(Prediction).join(Fixture).join(League).filter(
        Prediction.user_id == user_id,
        Fixture.league_id == league_id
    ).all()

    print(len(predictions))
    return predictions