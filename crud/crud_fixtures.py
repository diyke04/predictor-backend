import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists
from models.fixture import Fixture, FixtureStatus
from schemas.fixture import FixtureCreate
from models.prediction import Prediction
from fastapi import HTTPException, status
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from db.session import AsyncSessionLocal


async def get_fixture(db: AsyncSession, fixture_id: int):
    result = await db.execute(select(Fixture).filter(Fixture.id == fixture_id))
    fixture = result.scalars().first()
    if fixture:
        return fixture.to_dict()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")

async def get_fixtures_by_league(db: AsyncSession, league_id: int):
    result = await db.execute(select(Fixture).filter(Fixture.league_id == league_id))
    fixtures = result.scalars().all()
    return [fixture.to_dict() for fixture in fixtures]

async def get_fixtures_user_has_not_predicted_on(user_id: int, league: str, db: AsyncSession):
    subquery = select(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    result = await db.execute(
        select(Fixture).filter(
            Fixture.league == league,
            Fixture.status != FixtureStatus.COMPLETED,
            ~exists().where(Fixture.id == subquery.c.fixture_id)
        )
    )
    fixtures = result.scalars().all()
    return [fixture.to_dict() for fixture in fixtures]

async def delete_fixture(db: AsyncSession, fixture_id: int):
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

async def fetch_and_process(url: str, semaphore: asyncio.Semaphore, task_id: str,  callback):
    async with semaphore:
        async with AsyncSessionLocal() as db:
            try:
                print(url)
                await callback(db, task_id, "pending")
                print(url)
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    print(response.status_code)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table')
                    
                    if table is None:
                        raise ValueError("No table found on the webpage")
                    
                    df = pd.read_html(str(table))[0]
                    df = df.dropna(how='all')

                    df["key"] = df['Wk'].astype(str) + df['Home'] + df['Away'] 
                    df['Score'] = df['Score'].astype(str)  # Ensure 'Score' is a string

                    df['Home_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[0] if '-' in x else None)
                    df['Away_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[1] if '-' in x else None)

                    df['League'] = f"{url.split('/')[-1].split('-')[2]} {url.split('/')[-1].split('-')[3]}"

                    new_fixtures_to_add = []
                    print(df.head(2))
                 

                    for _, row in df.iterrows():
                        match_key = row['key']
                        match_week = row['Wk']
                        match_date = pd.to_datetime(row['Date'])
                        home_team = row['Home']
                        away_team = row['Away']
                        home_score = row['Home_Score']
                        away_score = row['Away_Score']
                        home_xg = row.get('xG', None)
                        away_xg = row.get('xG.1', None)
                        match_venue = row['Venue']
                        match_league = row['League']
                        match_attendance = row.get('Attendance', None)
                        match_referee = row.get('Referee', None)
                        match_day = row['Day']
                        match_time = row['Time']
                        match_score = row['Score']

                        fixture_data = FixtureCreate(
                            key=str(match_key),
                            week=str(match_week),
                            home_team=str(home_team),
                            away_team=str(away_team),
                            date=match_date,
                            venue=str(match_venue),
                            league=str(match_league)
                        )

                        # Check if fixture exists, then update or create new
                        results = await db.execute(select(Fixture).filter_by(key=match_key))
                        existing_fixture = results.scalars().first()

                        if not existing_fixture:
                            new_fixtures_to_add.append(Fixture(**fixture_data.model_dump()))

                        if existing_fixture:
                            # Update existing fixture if scores are available
                            if home_score is not None and away_score is not None:
                                existing_fixture.home_score = home_score
                                existing_fixture.away_score = away_score
                                existing_fixture.home_xg = home_xg
                                existing_fixture.away_xg = away_xg
                                existing_fixture.referee = match_referee
                                existing_fixture.attendance = match_attendance
                                existing_fixture.score = match_score
                                existing_fixture.day = match_day
                                existing_fixture.time = match_time

                                await db.commit()

                    if new_fixtures_to_add:
                        db.add_all(new_fixtures_to_add)
                        await db.commit()

                    # Call the callback function upon successful completion
                    await callback(db, task_id, "completed")
                    return {"status": "success", "message": "Fixtures updated"}
            
            except Exception as e:
                await callback(db, task_id, "failed")
                await db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add fixture: {str(e)}")
