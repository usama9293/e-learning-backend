from sqlalchemy import Column, Integer, String, Date, Text,DateTime
from app.db.base import Base
from datetime import datetime

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(Date)
    description = Column(Text)
    image=Column(String)
    status=Column(String,default="active")
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow)
