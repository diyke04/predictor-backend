from datetime import datetime
from pydantic import BaseModel

class FixtureCreate(BaseModel):
    home_team: str
    away_team: str
    match_date: datetime
    league: str

class FixtureUpdate(BaseModel):
    home_team_score: int
    away_team_score: int

class Fixture(BaseModel):
    id: int
    home_team: str
    away_team: str
    match_date: datetime
    league: str
    home_team_score: int | None
    away_team_score: int | None
    
    class Config:
        orm_mode = True
