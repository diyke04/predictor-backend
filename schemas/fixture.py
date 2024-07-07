from datetime import datetime
from pydantic import BaseModel
from schemas.league import League

class FixtureCreate(BaseModel):
    key:str
    week: str
    date: datetime
    home_team: str
    away_team: str
    venue: str
    league_id:int

class FixtureUpdate(BaseModel):
    score: str | None
    attendance: str | None
    referee: str | None
    home_xg: str | None
    away_xg: str | None
    home_score: str | None
    away_score: str | None

class FixtureSchema(BaseModel):
    id: int
    week: str
    date: datetime
    home_team: str
    away_team: str
    home_score: str | None
    away_score: str | None
    result:str|None
    status:str|None
    league:League

    
    class Config:
        from_attributes = True
