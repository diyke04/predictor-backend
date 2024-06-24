from sqlalchemy.sql import exists
from sqlalchemy.orm import Session
from models.fixture import Fixture,FixtureStatus
from schemas.fixture import FixtureCreate, FixtureUpdate
from models.prediction import Prediction
from reward import reward
from core.config import RewardType
from fastapi import HTTPException,status

async def create_fixture(db: Session, fixture: FixtureCreate):
    db_fixture = Fixture(**fixture.dict())
    db.add(db_fixture)
    db.commit()
    db.refresh(db_fixture)

    return db_fixture.to_dict()


async def get_fixture(db: Session, fixture_id: int):
    fixture= db.query(Fixture).filter(Fixture.id == fixture_id).first()
    return fixture.to_dict()


async def get_fixtures_by_league(db: Session, league_id: int):
    fixtures= db.query(Fixture).filter(Fixture.league_id==league_id).all()
    fixtures_response=[
        fixture.to_dict() for fixture in fixtures
    ]

    return fixtures_response

async def get_fixtures_user_has_not_predicted_on(user_id: int, league_id: int, db: Session):
    subquery = db.query(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    fixtures = db.query(Fixture).filter(
        Fixture.league_id == league_id,Fixture.status!="COMPLETED",
        ~exists().where(Fixture.id == subquery.c.fixture_id)
    ).all()
    fixtures_response = [
        fixture.to_dict()
        for fixture in fixtures
    ]
    
    return fixtures_response  

async def update_fixture_scores(db: Session, fixture_id: int, fixture_update: FixtureUpdate):
    db_fixture = db.query(Fixture).filter(Fixture.id==fixture_id).first()

    db_fixture.home_team_ft_score =fixture_update.home_team_ft_score
    db_fixture.away_team_ft_score=fixture_update.away_team_ft_score
    db_fixture.status=FixtureStatus.COMPLETED
    
    db.add(db_fixture)
    db.commit()
    db.refresh(db_fixture)

    for prediction in db_fixture.predictions:
        await reward.evaluate_prediction(prediction, db)

    return db_fixture.to_dict()

async def delete_fixture(db:Session,fixture_id):
    fixture =db.query(Fixture).filter(Fixture.id==fixture_id).first()
    
    db.delete(fixture)
    db.commit()
    return {
        "status": "deleted"
    }

   
