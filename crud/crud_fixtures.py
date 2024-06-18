from sqlalchemy.sql import exists
from sqlalchemy.orm import Session
from models.fixture import Fixture
from schemas.fixture import FixtureCreate, FixtureUpdate
from models.league import League
from models.prediction import Prediction

def create_fixture(db: Session, fixture: FixtureCreate):
    db_fixture = Fixture(**fixture.dict())
    db.add(db_fixture)
    db.commit()
    db.refresh(db_fixture)

    return db_fixture

def get_fixtures(db: Session):
    return db.query(Fixture).all()

def get_fixture(db: Session, fixture_id: int):
    return db.query(Fixture).filter(Fixture.id == fixture_id).first()

def get_fixtures_by_league(db: Session, league_id: int,user_id:int):
    return db.query(Fixture).filter(Fixture.league_id==league_id).all()

def get_fixtures_user_has_not_predicted_on(user_id: int, league_id: int, db: Session):
    subquery = db.query(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    fixtures = db.query(Fixture).filter(
        Fixture.league_id == league_id,
        ~exists().where(Fixture.id == subquery.c.fixture_id)
    ).all()
    fixtures_response = [
        {
            "id": fixture.id,
            "league_id": fixture.league_id,
            "league":fixture.league,
            "home_team": fixture.home_team,
            "away_team": fixture.away_team,
            "match_week": str(fixture.match_week),  # Convert match_week to string
            "match_date": fixture.match_date,
            "home_team_ft_score": fixture.home_team_ft_score,
            "away_team_ft_score": fixture.away_team_ft_score,
            "result": fixture.result()  # Ensure result is a string
        }
        for fixture in fixtures
    ]
    
    return fixtures_response  

def update_fixture(db: Session, fixture_id: int, fixture_update: FixtureUpdate):
    db_fixture = get_fixture(db, fixture_id)
    if not db_fixture:
        return None
    update_data = fixture_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_fixture, key, value)
    db.add(db_fixture)
    db.commit()
    db.refresh(db_fixture)
    return db_fixture
