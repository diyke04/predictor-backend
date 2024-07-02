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
    league:str

class FixtureUpdate(BaseModel):
    score: str | None
    attendance: str | None
    referee: str | None
    home_xg: str | None
    away_xg: str | None
    home_score: str | None
    away_score: str | None

class Fixture(BaseModel):
    id: int
    week: str
    day: str
    date: datetime
    time: str
    home_team: str
    away_team: str
    home_score: str | None
    away_score: str | None
    home_xg: float
    away_xg: float
    attendance: int | None
    venue: str
    referee: str | None
    
    class Config:
        from_attributes = True
