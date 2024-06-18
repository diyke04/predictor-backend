from datetime import datetime
from pydantic import BaseModel
from schemas.league import League

class FixtureCreate(BaseModel):
    home_team: str
    away_team: str
    match_date: datetime
    match_week:int
    league_id: int

class FixtureUpdate(BaseModel):
    home_team_ft_score: int
    away_team_ft_score: int

class Fixture(BaseModel):
    id: int
    home_team: str
    away_team: str
    match_week:int
    match_date: datetime
    league: League
    home_team_ft_score: int | None
    away_team_ft_score: int | None
    result:str
    
    class Config:
        from_attributes = True
