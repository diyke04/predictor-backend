from sqlalchemy import Column, Integer, String, DateTime,Boolean
from db.base import Base

class League(Base):
    __tablename__="leagues"

    id=Column(Integer,primary_key=True,index=True)
    name =Column(String,index=True)
    premium=Column(Boolean,default=False)

