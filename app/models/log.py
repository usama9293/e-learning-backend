from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    action = Column(String)
    user = Column(String)
