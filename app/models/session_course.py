from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class SessionCourse(Base):
    __tablename__ = "session_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    tutor_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="session_courses")
    session = relationship("Session", back_populates="session_courses")
    tutor = relationship("User", back_populates="session_courses")

    
