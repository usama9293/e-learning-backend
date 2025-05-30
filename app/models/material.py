from sqlalchemy import JSON,Column, Integer, String, ForeignKey,DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    file_path = Column(String, nullable=False)
    link = Column(String, nullable=False)
    # Relationships
    session = relationship("Session", back_populates="materials")
    