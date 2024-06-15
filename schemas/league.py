from pydantic import BaseModel

class LeagueBase(BaseModel):
    name: str

class LeagueCreate(LeagueBase):
    pass

class League(LeagueBase):
    id: int
    premium: bool
    

    class Config:
        from_attributes = True