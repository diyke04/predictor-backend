from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists
from models.fixture import Fixture, FixtureStatus
from schemas.fixture import FixtureCreate, FixtureUpdate
from models.prediction import Prediction
from reward import reward
from fastapi import HTTPException, status
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from db.session import AsyncSessionLocal

async def create_fixture(db: Session, fixture: FixtureCreate):
    try:
        db_fixture = Fixture(**fixture.dict())
        db.add(db_fixture)
        await db.commit()
        await db.refresh(db_fixture)
        return db_fixture.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create fixture: {str(e)}")

async def get_fixture(db: Session, fixture_id: int):
    fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()
    if fixture:
        return fixture.to_dict()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")

async def get_fixtures_by_league(db: Session, league_id: int):
    fixtures = db.query(Fixture).filter(Fixture.league_id == league_id).all()
    return [fixture.to_dict() for fixture in fixtures]

async def get_fixtures_user_has_not_predicted_on(user_id: int, league_id: int, db: Session):
    subquery = db.query(Prediction.fixture_id).filter(Prediction.user_id == user_id).subquery()
    fixtures = db.query(Fixture).filter(
        Fixture.league_id == league_id,
        Fixture.status != FixtureStatus.COMPLETED,
        ~exists().where(Fixture.id == subquery.c.fixture_id)
    ).all()
    return [fixture.to_dict() for fixture in fixtures]

async def update_fixture_scores(db: Session, fixture_id: int, fixture_update: FixtureUpdate):
    try:
        db_fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if db_fixture:
            db_fixture.home_score = fixture_update.home_score
            db_fixture.away_score = fixture_update.away_score
            db_fixture.status = FixtureStatus.COMPLETED

            await db.commit()
            await db.refresh(db_fixture)

            for prediction in db_fixture.predictions:
                await reward.evaluate_prediction(prediction, db)

            return db_fixture.to_dict()

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update fixture: {str(e)}")

async def delete_fixture(db: Session, fixture_id: int):
    try:
        fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if fixture:
            db.delete(fixture)
            await db.commit()
            return {"status": "deleted"}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found")
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete fixture: {str(e)}")

async def fetch_and_process(url: str):
    async with AsyncSessionLocal() as db:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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
                existing_fixtures_to_update = []

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
                    print("Adding to db new fixtures")
                    await db.commit()
                

                

                return {"status": "success", "message": "Fixtures updated"}
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add fixture: {str(e)}")
