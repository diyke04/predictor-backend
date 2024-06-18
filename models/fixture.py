from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime

class Fixture(Base):
    __tablename__ = "fixtures"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    home_team = Column(String(100), index=True)
    away_team = Column(String(100), index=True)
    match_week = Column(Integer, index=True)
    match_date = Column(DateTime)
    home_team_ft_score = Column(Integer, nullable=True)
    away_team_ft_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  
    league = relationship('League', back_populates='fixtures')
    predictions = relationship('Prediction', back_populates='fixture')

    def result(self):
        if self.home_team_ft_score and self.away_team_ft_score is not None:
            if self.home_team_ft_score > self.away_team_ft_score:
                return 'home'
            elif self.away_team_ft_score > self.home_team_ft_score:
                return 'away'
            else:
                return 'draw'
        return 'no result'
