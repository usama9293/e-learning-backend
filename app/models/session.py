from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from sqlalchemy.dialects.sqlite import JSON 

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    description = Column(String)
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    days = Column(JSON) 
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    tutor_info_id = Column(Integer, ForeignKey("tutor_info.id"))

    # Direct relationships
    course = relationship("Course", back_populates="sessions")
    tutor = relationship("TutorInfo", back_populates="sessions")
    students = relationship("StudentInfo", back_populates="sessions", secondary="session_students")
    materials = relationship("Material", back_populates="session")
    assignments = relationship("Assignment", back_populates="session")
    @property
    def full_name(self):
        return self.tutor.full_name

    @property
    def course_name(self):
        return self.course.name

# Association table for many-to-many relationship between Session and StudentInfo
class SessionStudent(Base):
    __tablename__ = "session_students"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("student_info.id"))
    status = Column(String)  # attended, absent, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
