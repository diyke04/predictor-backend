from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Enum as SQLEnum
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime

class FixtureStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    POSTPONED = "postponed"

class Fixture(Base):
    __tablename__ = "fixtures"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    home_team = Column(String(100), index=True)
    away_team = Column(String(100), index=True)
    match_week = Column(Integer, index=True)
    match_date = Column(DateTime)
    home_team_ft_score = Column(String(10), nullable=True)
    away_team_ft_score = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  
    league = relationship('League', back_populates='fixtures')
    predictions = relationship('Prediction', back_populates='fixture')
    status = Column(SQLEnum(FixtureStatus), default=FixtureStatus.SCHEDULED)

    def result(self):
        if self.home_team_ft_score and self.away_team_ft_score is not None:
            if self.home_team_ft_score > self.away_team_ft_score:
                return 'home'
            elif self.away_team_ft_score > self.home_team_ft_score:
                return 'away'
            else:
                return 'draw'
        return 'no result'
    
    def to_dict(self):
        return {
            "id": self.id,
            "league": self.league.to_dict(),
            "home_team": self.home_team,
            "away_team": self.away_team,
            "match_week": self.match_week,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "home_team_ft_score": self.home_team_ft_score,
            "away_team_ft_score": self.away_team_ft_score,
            "result": self.result() if self.result else None,
            "status": self.status.value
        }

