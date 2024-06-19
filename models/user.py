from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String(100), unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    predictions = relationship('Prediction', back_populates='user')
    point = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "email":self.email,
            "username": self.username,
            "point":self.point,
            
        }
