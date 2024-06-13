import pydantic as _pydantic
import datetime as _dt

class _MatchBase(_pydantic.BaseModel):
    date:str
    away_team:str
    home_team:str


class MatcheCreate(_MatchBase):
    pass

class Match(_MatchBase):
    id:int
    away_team_score_prediction:int | None
    home_team_score_prediction:int | None
    away_team_score_ft:int | None
    home_team_score_ft:int | None
    result:str | None

    class Config:
        from_attributes =True


class _UserBase(_pydantic.BaseModel):
    username:str

class UserCreate(_UserBase):
    password:str

class User(_UserBase):
    id:int

    class Config:
        from_attributes=True

