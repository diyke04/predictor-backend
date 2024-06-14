from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import crud_fixtures
from schemas.fixture import FixtureCreate, Fixture, FixtureUpdate
from db.session import get_db

router = APIRouter()

@router.post("/", response_model=Fixture)
def create_fixture(fixture: FixtureCreate, db: Session = Depends(get_db)):
    return crud_fixtures.create_fixture(db=db, fixture=fixture)

@router.get("/", response_model=List[Fixture])
def read_fixtures(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_fixtures.get_fixtures(db=db, skip=skip, limit=limit)

@router.get("/{fixture_id}", response_model=Fixture)
def read_fixture(fixture_id: int, db: Session = Depends(get_db)):
    db_fixture = crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture

@router.put("/{fixture_id}", response_model=Fixture)
def update_fixture(fixture_id: int, fixture_update: FixtureUpdate, db: Session = Depends(get_db)):
    db_fixture = crud_fixtures.update_fixture(db=db, fixture_id=fixture_id, fixture_update=fixture_update)
    if not db_fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return db_fixture
