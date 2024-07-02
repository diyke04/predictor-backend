import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependency import is_superuser, get_current_user
from crud import crud_fixtures
from schemas.fixture import FixtureCreate, Fixture, FixtureUpdate
from db.session import get_db
from core.config import urls

router = APIRouter()

@router.post("/", response_model=Fixture)
async def create_fixture(fixture: FixtureCreate, db: AsyncSession = Depends(get_db), admin: bool = Depends(is_superuser)):
    if admin:
        return await crud_fixtures.create_fixture(db=db, fixture=fixture)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

@router.get("/{fixture_id}", response_model=Fixture)
async def read_fixture(fixture_id: int, db: Session = Depends(get_db)):
    db_fixture = await crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")
    return db_fixture

@router.get("/league/{league_id}", response_model=List[Fixture])
async def get_league_fixtures(league_id: int, db: Session = Depends(get_db)):
    db_fixtures = await crud_fixtures.get_fixtures_by_league(db=db, league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixtures not found")
    return db_fixtures

@router.get("/user/not-predicted", response_model=List[Fixture])
async def get_fixtures_user_not_predicted(league_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_fixtures = await crud_fixtures.get_fixtures_user_has_not_predicted_on(user_id=user.id, db=db, league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixtures not found")
    return db_fixtures

@router.delete("/{fixture_id}", response_model=dict)
async def delete_fixture(fixture_id: int, db: Session = Depends(get_db)):
    result = await crud_fixtures.delete_fixture(db=db, fixture_id=fixture_id)
    if result:
        return {"status": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")

@router.put("/{fixture_id}", response_model=Fixture)
async def update_fixture_scores(fixture_id: int, fixture_update: FixtureUpdate, db: Session = Depends(get_db)):
    db_fixture = await crud_fixtures.update_fixture_scores(db=db, fixture_id=fixture_id, fixture_update=fixture_update)
    if not db_fixture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")
    return db_fixture

@router.post("/scrape", response_model=dict)
async def scrape_and_update_fixtures():

    tasks = [crud_fixtures.fetch_and_process(url) for url in urls]
    await asyncio.gather(*tasks)

    return {"message": "Fixtures scraped and updated successfully."}