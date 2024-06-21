from sqlalchemy import Column, Integer, ForeignKey,String
from sqlalchemy.orm import relationship
from db.base import Base
from core.config import RewardType


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    home_prediction_score = Column(String(10))
    away_prediction_score = Column(String(10))
    fixture = relationship('Fixture', back_populates='predictions')
    user = relationship('User', back_populates='predictions')


    def result(self):
        if self.home_prediction_score and self.away_prediction_score is not None:
            if self.home_prediction_score > self.away_prediction_score:
                return 'home'
            elif self.away_prediction_score > self.home_prediction_score:
                return 'away'
            else:
                return 'draw'
        return 'no prediction'
        
    def correct_score(self):
        if self.fixture.home_team_ft_score and self.fixture.away_team_ft_score and self.home_prediction_score and self.away_prediction_score is not None:
            
            if (self.fixture.home_team_ft_score == self.home_prediction_score) and (self.fixture.away_team_ft_score == self.away_prediction_score):
                return 'correct'

        return 'not correct'
    

    
    def to_dict(self):
        return {
            "id": self.id,
            "home_prediction_score": self.home_prediction_score,
            "away_prediction_score": self.away_prediction_score,
            "user": self.user.to_dict() if self.user else None,
            "fixture": self.fixture.to_dict() if self.fixture else None,
            "result":self.result(),
            "correct_score":self.correct_score(),

        }
