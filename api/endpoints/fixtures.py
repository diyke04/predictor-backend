
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependency import  get_current_user
from crud import crud_fixtures
from schemas.fixture import Fixture
from db.session import AsyncSessionLocal, get_db
from core.config import urls,semaphore
import uuid
from models.services import TaskStatus
from schemas.service import TaskStatusResponse
from crud import services

router = APIRouter()



@router.get("/{fixture_id}", response_model=Fixture)
async def read_fixture(fixture_id: int, db: AsyncSession = Depends(get_db)):
    db_fixture = await crud_fixtures.get_fixture(db=db, fixture_id=fixture_id)
    if not db_fixture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")
    return db_fixture
    

@router.get("/league/{league_id}", response_model=List[Fixture])
async def get_league_fixtures(league_id: int, db: AsyncSession = Depends(get_db)):
    db_fixtures = await crud_fixtures.get_fixtures_by_league(db=db, league_id=league_id)
    if not db_fixtures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixtures not found")
    return db_fixtures

@router.get("/user/not-predicted", response_model=List[Fixture])
async def get_fixtures_user_not_predicted(league: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    db_fixtures = await crud_fixtures.get_fixtures_user_has_not_predicted_on(user_id=user.id, db=db, league=league)
    if not db_fixtures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixtures not found")
    return db_fixtures

@router.delete("/{fixture_id}", response_model=dict)
async def delete_fixture(fixture_id: int, db: AsyncSession = Depends(get_db)):
    result = await crud_fixtures.delete_fixture(db=db, fixture_id=fixture_id)
    if result:
        return {"status": "deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found")


@router.post("/scrape", response_model=dict)
async def scrape_and_update_fixtures(background_tasks: BackgroundTasks):
    task_ids = []

    for url in urls:
        task_id = str(uuid.uuid4())
        task_ids.append(task_id)
        background_tasks.add_task(crud_fixtures.fetch_and_process, url, semaphore, task_id, services.update_task_status)

    return {"message": "Fixtures scraping and updating initiated.", "task_ids": task_ids}




@router.get("/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: AsyncSession = Depends(AsyncSessionLocal)):
    task_status = await db.get(TaskStatus, task_id)
    if task_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task ID not found")
    return TaskStatusResponse(task_id=task_id, status=task_status.status)