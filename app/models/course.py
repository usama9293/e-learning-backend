from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    schedule_date = Column(String)
    schedule_time = Column(String)
    is_active = Column(Boolean, default=True)
    image = Column(String)
    price = Column(DECIMAL)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Direct relationships
    sessions = relationship("Session", back_populates="course")
    tutors = relationship("TutorInfo", back_populates="courses", secondary="course_tutors")
    students = relationship("StudentInfo", back_populates="courses", secondary="course_students")
    
# Association table for many-to-many relationship between Course and TutorInfo
class CourseTutor(Base):
    __tablename__ = "course_tutors"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    tutor_id = Column(Integer, ForeignKey("tutor_info.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# Association table for many-to-many relationship between Course and StudentInfo
class CourseStudent(Base):
    __tablename__ = "course_students"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    student_id = Column(Integer, ForeignKey("student_info.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def assigned_tutors(self):
        return [session.tutor for session in self.session_courses]
    @property
    def assigned_sessions(self):
        return [session.session for session in self.session_courses]
    @property
    def assigned_students(self):
        return [student.student for student in self.enrolled_students]





   
    
    
    

