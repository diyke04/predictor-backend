from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crud import crud_league
from schemas.league import League,LeagueCreate
from db.session import get_db

router = APIRouter()

@router.post("/", response_model=League)
def create_league(league: LeagueCreate, db: Session = Depends(get_db)):
    return crud_league.create_league(db=db, league=league)
