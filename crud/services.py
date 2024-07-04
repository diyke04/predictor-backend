from typing import List
from bs4 import BeautifulSoup
import httpx
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from models.services import TaskStatus
from schemas .fixture import Fixture,FixtureCreate
from utils.send_mail import send_local_email



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

def update_existing_fixture(existing_fixture: Fixture, fixture_data: FixtureCreate):
    existing_fixture.home_score = fixture_data.home_score
    existing_fixture.away_score = fixture_data.away_score
    existing_fixture.home_xg = fixture_data.home_xg
    existing_fixture.away_xg = fixture_data.away_xg
    existing_fixture.referee = fixture_data.referee
    existing_fixture.attendance = fixture_data.attendance
    existing_fixture.score = fixture_data.score
    existing_fixture.day = fixture_data.day
    existing_fixture.time = fixture_data.time

async def fetch_fixtures(url: str) -> pd.DataFrame:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if table is None:
            raise ValueError("No table found on the webpage")
        df = pd.read_html(str(table))[0]
        df = df.dropna(how='all')
        return df

def process_fixture_data(df: pd.DataFrame, url: str) -> List[FixtureCreate]:
    df["key"] = df['Wk'].astype(str) + df['Home'] + df['Away']
    df['Score'] = df['Score'].astype(str)
    df['Home_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[0] if '-' in x else None)
    df['Away_Score'] = df['Score'].apply(lambda x: x.replace('–', '-').split('-')[1] if '-' in x else None)
    df['League'] = f"{url.split('/')[-1].replace('-Scores-and-Fixtures','').replace('-',' ')}"

    
    fixtures_to_add = []
    for _, row in df.iterrows():
        fixture_data = FixtureCreate(
            key=str(row['key']),
            week=str(row['Wk']),
            home_team=str(row['Home']),
            away_team=str(row['Away']),
            date=pd.to_datetime(row['Date']),
            venue=str(row['Venue']),
            league=str(row['League'])
        )
        fixtures_to_add.append(fixture_data)
    return fixtures_to_add




