from sqlalchemy.orm import Session
from models.league import League
from schemas.league import LeagueCreate

def create_league(db: Session, league: LeagueCreate):
    
    db_league = League(name=league.name)
    db.add(db_league)
    db.commit()
    db.refresh(db_league)
    return db_league

def get_league_by_id(db: Session, id: int):
    return db.query(League).filter(League.id== id).first()

def get_leagues(db:Session):
    return db.query(League).all()
