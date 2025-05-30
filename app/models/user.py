from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime
import json
class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    student_info = relationship("StudentInfo", back_populates="user", uselist=False)
    tutor_info = relationship("TutorInfo", back_populates="user", uselist=False)
    submissions = relationship("Submission", back_populates="student")
    course_chats = relationship("CourseChats", back_populates="members", secondary="course_members")

    course_memberships = relationship(
        "CourseMembers",
        back_populates="user",
        overlaps="course_chats"
    )

    # Relationship to CourseChats (many-to-many via CourseMembers)
    course_chats = relationship(
        "CourseChats",
        secondary="course_members",
        primaryjoin="User.id == CourseMembers.user_id",
        secondaryjoin="CourseChats.course_id == CourseMembers.course_id",
        back_populates="members"
    )

    # sent_messages = relationship("TutorStudentMessage", foreign_keys="[TutorStudentMessage.chat_id]")
    # enrolled_courses = relationship("StudentCourse", back_populates="student")
    # session_courses = relationship("SessionCourse", back_populates="tutor")
    # sessions = relationship("SessionStudent", back_populates="student")
    def to_dict(self):
        if self.role == 'student':
            info = self.student_info.to_dict()
        elif self.role == 'tutor':
            info = self.tutor_info.to_dict()
        else:
            info = {}
        return {
            'id':self.id,
            'email':self.email,
           'full_name':self.full_name,
           'info':info
           
        }

# models/student_info.py
class StudentInfo(Base):
    __tablename__ = "student_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    contact_number = Column(String)
    address = Column(String)
    grade_level = Column(String)
    emergency_contact = Column(String)
    parent_guardian = Column(String)
    # Direct relationships
    user = relationship("User", back_populates="student_info")
    courses = relationship("Course", back_populates="students", secondary="course_students")
    sessions = relationship("Session", back_populates="students", secondary="session_students")

    def to_dict(self):
        keys = 'id full_name dob gender contact_number address grade_level emergency_contact parent_guardian'
        info =  {
        }
        for k in keys.split(' '):
            info[k] = self.__getattribute__(k)
        return info


# models/tutor_info.py
class TutorInfo(Base):
    __tablename__ = "tutor_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    contact_number = Column(String)
    address = Column(String)
    # Direct relationships
    user = relationship("User", back_populates="tutor_info")
    courses = relationship("Course", back_populates="tutors", secondary="course_tutors")
    sessions = relationship("Session", back_populates="tutor")
    
    def __repr__(self):
        return f"{self.full_name}"

    def to_dict(self):
        keys = 'id full_name dob gender contact_number address'
        info =  {
        }
        
        for k in keys.split(' '):
            k = k.strip()
            if k:
                info[k] = self.__getattribute__(k)
        print(info)
        return info
