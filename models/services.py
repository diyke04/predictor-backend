from sqlalchemy import Column, String, DateTime, Enum
from datetime import datetime
from db.base import Base

class TaskStatus(Base):
    __tablename__ = 'task_statuses'
    task_id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
