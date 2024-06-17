from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.base import Base

class League(Base):
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    premium = Column(Boolean, default=False)
    
    fixtures = relationship('Fixture', back_populates='league')
