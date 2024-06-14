from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base

class Fixture(Base):
    __tablename__ = "fixtures"
    
    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    match_date = Column(DateTime)
    league = Column(String)
    home_team_score = Column(Integer, nullable=True)
    away_team_score = Column(Integer, nullable=True)
