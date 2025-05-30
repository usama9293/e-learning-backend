from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class SessionStudent(Base):
    __tablename__ = "session_student"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    
    session = relationship("Session", back_populates="students")
    students = relationship("User", back_populates="sessions")
    status = Column(String)  # attended, absent, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="students")
    student = relationship("User", back_populates="sessions")
