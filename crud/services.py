from bs4 import BeautifulSoup
from fastapi import HTTPException,status
import httpx
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from models.services import TaskStatus
from models.fixture import FixtureStatus,Fixture
from models.league import League
from schemas .fixture import FixtureCreate
from schemas.league import LeagueCreate
from utils.send_mail import send_local_email
from crud import crud_league



async def update_task_status(db: AsyncSession, task_id: str, status: str):
    
    task_status = await db.get(TaskStatus, task_id)
    if task_status:
        task_status.status = status
        
        # Send an email notification to the admin
        admin_email = "iykedave04@gmail.com"
        subject = f"Task {task_id} Status Update"
        body = f"The task with ID {task_id} has {status}."
        send_local_email(sender_email="iyke04@gmail.com",
                         receiver_email=admin_email,
                         subject=subject,
                         body=body
                         )
    else:
        task_status = TaskStatus(task_id=task_id, status=status)
        db.add(task_status)

    await db.commit()

async def fetch_and_process(url: str, task_id: str,db):
  try:
    await update_task_status(db, task_id, "pending")
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

        df['Home_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[0] if '–' in x else None)
        df['Away_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[1] if '–' in x else None)

        parts = url.split("/")[-1].replace("-Scores-and-Fixtures", '').split("-")
        league_name = " ".join(part for part in parts if not part.isdigit())

        df['League'] = league_name

        return df
  except Exception as e:
        await update_task_status(db, task_id, "failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add fixture: {str(e)}")


async def process_fixture_data(db: AsyncSession, row: pd.Series, match_key: str):
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
    

    
    league_exist=await crud_league.get_league_by_id(db,match_league)
    if league_exist:
        league_id=league_exist.id
    else:
        league=LeagueCreate(name=match_league)
        response=await crud_league.create_league(db,league)
        league_id=response.id
        


    fixture_data = FixtureCreate(
        key=str(match_key),
        week=str(match_week),
        home_team=str(home_team),
        away_team=str(away_team),
        date=match_date,
        venue=str(match_venue),
        league_id=league_id
    )

    results = await db.execute(select(Fixture).filter_by(key=match_key))
    existing_fixture = results.scalars().first()

    if not existing_fixture:
        return {'new': True, 'data': fixture_data.dict()}

    if home_score and away_score is not None:
        existing_fixture.home_score = home_score
        existing_fixture.away_score = away_score
        existing_fixture.home_xg = home_xg
        existing_fixture.away_xg = away_xg
        existing_fixture.referee = match_referee
        existing_fixture.attendance = match_attendance
        existing_fixture.score = match_score
        existing_fixture.day = match_day
        existing_fixture.time = match_time
        existing_fixture.status = FixtureStatus.COMPLETED

    return {'new': False, 'data': existing_fixture}




