from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from api.dependency import is_superuser,get_current_user
from crud import crud_fixtures
from schemas.fixture import FixtureCreate, Fixture, FixtureUpdate
from db.session import get_db


router = APIRouter()

@router.post("/", response_model=Fixture)
async def create_fixture(fixture: FixtureCreate, db: Session = Depends(get_db),admin=True):
    if admin:
        return await crud_fixtures.create_fixture(db=db, fixture=fixture)
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Not Authorised")


@router.get("/", response_model=Fixture)
async def read_fixture(fixture_id: int, db: Session = Depends(get_db)):
    db_fixture = await crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture

@router.get("/league", response_model=List[Fixture])
async def get_league_fixtures(league_id: int, db: Session = Depends(get_db),):
    db_fixtures = await crud_fixtures.get_fixtures_by_league(db=db,league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixtures

@router.get("/user/not-predicted", response_model=List[Fixture])
async def get_fixtures_user_not_predicted(league_id:int, db: Session = Depends(get_db),user=Depends(get_current_user)):
    print("user",user)
    db_fixtures = await crud_fixtures.get_fixtures_user_has_not_predicted_on(user_id=user.id,db=db,league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixtures

@router.delete("/delete", response_model=Fixture)
async def delete_fixture(fixture_id: int, db: Session = Depends(get_db)):
    return await crud_fixtures.delete_fixture(db=db,fixture_id=fixture_id)

@router.put("/update", response_model=Fixture)
async def update_fixture_scores(fixture_id: int, fixture_update: FixtureUpdate, db: Session = Depends(get_db)):
    db_fixture = await crud_fixtures.update_fixture_scores(db=db, fixture_id=fixture_id, fixture_update=fixture_update)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture
