import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists
from models.fixture import Fixture, FixtureStatus
from schemas.fixture import FixtureCreate
from models.prediction import Prediction
from fastapi import HTTPException, status, APIRouter
from .services import update_existing_fixture,fetch_fixtures,process_fixture_data
from db.session import AsyncSessionLocal

from typing import List, Dict

router = APIRouter()

# Utility function to convert fixture to dictionary
def fixture_to_dict(fixture: Fixture) -> Dict:
    return fixture.to_dict()

async def get_fixture(db: AsyncSession, fixture_id: int) -> Dict:
    result = await db.execute(select(Fixture).filter(Fixture.id == fixture_id))
    fixture = result.scalars().first()
    if fixture:
        return fixture_to_dict(fixture)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")

async def get_fixtures_by_league(db: AsyncSession, league_id: int) -> List[Dict]:
    result = await db.execute(select(Fixture).filter(Fixture.league_id == league_id))
    fixtures = result.scalars().all()
    return [fixture_to_dict(fixture) for fixture in fixtures]

async def get_fixtures_user_has_not_predicted_on(user_id: int, league: str, db: AsyncSession) -> List[Dict]:
    subquery = select(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    result = await db.execute(
        select(Fixture).filter(
            Fixture.league == league,
            Fixture.status != FixtureStatus.COMPLETED,
            ~exists().where(Fixture.id == subquery.c.fixture_id)
        )
    )
    fixtures = result.scalars().all()
    return [fixture_to_dict(fixture) for fixture in fixtures]

async def delete_fixture(db: AsyncSession, fixture_id: int) -> Dict:
    try:
        result = await db.execute(select(Fixture).filter(Fixture.id == fixture_id))
        fixture = result.scalars().first()
        if fixture:
            await db.delete(fixture)
            await db.commit()
            return {"status": "deleted"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete fixture: {str(e)}")

async def fetch_and_process(url: str, semaphore: asyncio.Semaphore, task_id: str, callback):
    async with semaphore:
        async with AsyncSessionLocal() as db:
            try:
                await callback(db, task_id, "pending")
                df = await fetch_fixtures(url)
                fixtures = process_fixture_data(df, url)
                await update_or_create_fixtures(db, fixtures)
                await callback(db, task_id, "completed")
                return {"status": "success", "message": "Fixtures updated"}
            except Exception as e:
                await callback(db, task_id, "failed")
                await db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add fixture: {str(e)}")



async def update_or_create_fixtures(db: AsyncSession, fixtures: List[FixtureCreate]):
    new_fixtures = []
    for fixture_data in fixtures:
        existing_fixture = await db.execute(select(Fixture).filter_by(key=fixture_data.key)).scalars().first()
        if not existing_fixture:
            new_fixtures.append(Fixture(**fixture_data.model_dump()))
        else:
            update_existing_fixture(existing_fixture, fixture_data)
            await db.commit()
    if new_fixtures:
        db.add_all(new_fixtures)
        await db.commit()


