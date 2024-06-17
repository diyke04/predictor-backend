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
    # Subquery to get all fixture ids the user has predicted on
    subquery = db.query(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    
    # Main query to get fixtures where the user has not made a prediction
    fixtures = db.query(Fixture).filter(
        Fixture.league_id == league_id,
        ~exists().where(Fixture.id == subquery.c.fixture_id)
    ).all()
    
    return fixtures   

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
