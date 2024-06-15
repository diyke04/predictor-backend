from sqlalchemy.orm import Session
from models.fixture import Fixture
from schemas.fixture import FixtureCreate, FixtureUpdate
from models.league import League

def create_fixture(db: Session, fixture: FixtureCreate):
    db_fixture = Fixture(**fixture.dict())
    db.add(db_fixture)
    db.commit()
    db.refresh(db_fixture)

    return db_fixture

def get_fixtures(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Fixture).offset(skip).limit(limit).all()

def get_fixture(db: Session, fixture_id: int):
    return db.query(Fixture).filter(Fixture.id == fixture_id).first()

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
