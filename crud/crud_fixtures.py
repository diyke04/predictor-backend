import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import exists
from models.fixture import Fixture, FixtureStatus
from models.prediction import Prediction
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from db.session import AsyncSessionLocal
from .services import process_fixture_data,fetch_and_process

now = datetime.now()
seven_days_from_now = now + timedelta(days=7)

async def get_fixture(db: AsyncSession, fixture_id: int):
    result = await db.execute(select(Fixture).filter(Fixture.id == fixture_id))
    fixture = result.scalars().first()
    if fixture:
        return fixture.to_dict()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")


async def get_fixtures_by_league(db: AsyncSession, league_id: int):
    result = await db.execute(select(Fixture).filter(Fixture.league_id == league_id,Fixture.date.between(now, seven_days_from_now),))
    fixtures = result.scalars().all()
    return [fixture.to_dict() for fixture in fixtures]



async def get_fixtures_user_has_not_predicted_on(user_id: int, db: AsyncSession):
    now = datetime.utcnow()
    seven_days_from_now = now + timedelta(days=7)
    
    subquery = select(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    
    result = await db.execute(
        select(Fixture)
        .options(selectinload(Fixture.league))
        .filter(
            Fixture.status != FixtureStatus.COMPLETED,
            Fixture.date.between(now, seven_days_from_now),
            ~exists().where(Fixture.id == subquery.c.fixture_id)
        )
    )
    
    fixtures = result.scalars().all()
    return [fixture.to_dict() for fixture in fixtures]

async def delete_fixture(db: AsyncSession, fixture_id: int):
    async with db.begin():
        result = await db.execute(select(Fixture).filter(Fixture.id == fixture_id))
        fixture = result.scalars().first()
        if fixture:
            await db.delete(fixture)
            await db.commit()
            return {"status": "deleted"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")


async def create_update_fixtures(url: str, semaphore: asyncio.Semaphore,task_id: str,callback):
    new_fixtures_to_add = []
    all_existing_fixtures = []
    async with semaphore:
        async with AsyncSessionLocal() as db:

            df=await fetch_and_process(url=url,task_id=task_id,db=db)
            
            for _, row in df.iterrows():
                match_key = row['key']
                fixture_data = await process_fixture_data(db, row, match_key)

                if fixture_data['new']:
                    new_fixtures_to_add.append(Fixture(**fixture_data['data']))
                else:
                    all_existing_fixtures.append(fixture_data['data'])

            if new_fixtures_to_add:
                db.add_all(new_fixtures_to_add)

            if all_existing_fixtures:
                db.add_all(all_existing_fixtures)

            await db.commit()

            await callback(db, task_id, "completed")
            return {"status": "success", "message": "Fixtures updated"}

   
