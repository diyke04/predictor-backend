from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from api.dependency import is_superuser,get_current_user
from crud import crud_fixtures
from schemas.fixture import FixtureCreate, Fixture, FixtureUpdate
from db.session import get_db


router = APIRouter()

@router.post("/", response_model=Fixture)
def create_fixture(fixture: FixtureCreate, db: Session = Depends(get_db),admin=True):
    if admin:
        return crud_fixtures.create_fixture(db=db, fixture=fixture)
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Not Authorised")

@router.get("/", response_model=List[Fixture])
def read_fixtures( db: Session = Depends(get_db)):
    return crud_fixtures.get_fixtures(db=db)

@router.get("/{fixture_id}", response_model=Fixture)
def read_fixture(fixture_id: int, db: Session = Depends(get_db)):
    db_fixture = crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture

@router.get("/league/{league_id}", response_model=List[Fixture])
def get_league_fixtures(league_id: int, db: Session = Depends(get_db),user=Depends(get_current_user)):
    db_fixtures = crud_fixtures.get_fixtures_by_league(db=db,league_id=league_id,user_id=user.id)
    if not db_fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixtures

@router.get("/not-predicted/", response_model=List[Fixture])
def get_fixtures_not_predicted(league_id:int, db: Session = Depends(get_db),user=Depends(get_current_user)):
    print("user",user)
    db_fixtures = crud_fixtures.get_fixtures_user_has_not_predicted_on(user_id=user.id,db=db,league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixtures

@router.delete("/{fixture_id}", response_model=Fixture)
def delete_fixture(fixture_id: int, db: Session = Depends(get_db)):
    db_fixture = crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    
    db.delete(db_fixture)
    db.commit()
    return {"status":True}

@router.put("/{fixture_id}", response_model=Fixture)
def update_fixture(fixture_id: int, fixture_update: FixtureUpdate, db: Session = Depends(get_db)):
    db_fixture = crud_fixtures.update_fixture(db=db, fixture_id=fixture_id, fixture_update=fixture_update)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture
