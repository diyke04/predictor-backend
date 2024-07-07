from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from crud import crud_league
from schemas.league import League,LeagueCreate
from db.session import get_db

from typing import List

router = APIRouter()

@router.post("/", response_model=League)
async def create_league(league: LeagueCreate, db: Session = Depends(get_db)):
    return crud_league.create_league(db=db, league=league)


@router.get('/',response_model=List[League])
async def get_leagues(db:Session=Depends(get_db)):
    return await crud_league.get_leagues(db=db)