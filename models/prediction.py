from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from models.fixture import Fixture
from models.user import User

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    home_prediction_score = Column(Integer)
    away_prediction_score = Column(Integer)
    fixture = relationship(Fixture)
    user=relationship(User)

