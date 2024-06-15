from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from models.league import League

class Fixture(Base):
    __tablename__ = "fixtures"
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer,ForeignKey('leagues.id'))
    league= relationship(League)
    home_team = Column(String, index=True)
    away_team = Column(String, index=True)
    match_date = Column(DateTime)
    home_team_ft_score = Column(Integer, nullable=True)
    away_team_ft_score = Column(Integer, nullable=True)

