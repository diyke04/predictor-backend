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
    key = Column(String(220), index=True)
    week = Column(String(10), index=True)
    day = Column(String(10), nullable=True)
    date = Column(DateTime)
    time = Column(String(10), nullable=True)
    home_team = Column(String(100), index=True)
    home_score = Column(String(10), nullable=True)
    home_xg = Column(String(10), nullable=True)
    score = Column(String(10), nullable=True)
    away_score = Column(String(10), nullable=True)
    away_xg = Column(String(10), nullable=True)
    away_team = Column(String(100), index=True)
    attendance = Column(Integer, nullable=True)
    venue = Column(String(100))
    referee = Column(String(100), nullable=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    predictions = relationship('Prediction', back_populates='fixture')
    league = relationship('League', back_populates='fixtures')
    status = Column(SQLEnum(FixtureStatus), default=FixtureStatus.SCHEDULED)

    def result(self):
        if self.home_score is not None and self.away_score is not None:
            if int(self.home_score) > int(self.away_score):
                return 'home'
            elif int(self.away_score) > int(self.home_score):
                return 'away'
            else:
                return 'draw'
        return 'no result'
    
    def to_dict(self):
        
        return {
            "id": self.id,
            "week": self.week,
            "date": self.date,
            "league": self.league.to_dict() if self.league else None,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "result": self.result() if self.result else None,
            "status": self.status.value
        }

