from app.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    student_id = Column(Integer, ForeignKey("student_info.id"))
    tutor_id = Column(Integer, ForeignKey("tutor_info.id"))
    is_read = Column(Boolean, default=False)
    is_group = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))

class CourseChats(Base):
    __tablename__= "coursechats"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    course_id = Column(Integer, ForeignKey("courses.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    members = relationship(
        "User",
        secondary="course_members",
        primaryjoin="CourseChats.course_id == CourseMembers.course_id",
        secondaryjoin="User.id == CourseMembers.user_id",
        back_populates="course_chats",
        overlaps="course_memberships"
    )

class CourseMembers(Base):
    __tablename__ = "course_members"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="course_memberships",overlaps="course_chats,members")
    def __repr__(self):
        return f"<CourseMembers(id={self.id}, course_id={self.course_id}, user_id={self.user_id}, created_at={self.created_at})>"



class TutorStudentMessage(Base):
    __tablename__ = "tutor_student_messages"

    id = Column(Integer, primary_key=True) 
    chat_id = Column(Integer, ForeignKey("chats.id"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    def __repr__(self):
        return f"<TutorStudentMessage(id={self.id}, chat_id={self.chat_id}, message={self.message}, created_at={self.created_at}, is_read={self.is_read})>"

class AdminTutorMessage(Base):
    __tablename__ = "admin_tutor_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    def __repr__(self):
        return f"<AdminTutorMessage(id={self.id}, chat_id={self.chat_id}, message={self.message}, created_at={self.created_at}, is_read={self.is_read})>"


class AdminStudentMessage(Base):
    __tablename__ = "admin_student_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    def __repr__(self):
        return f"<AdminStudentMessage(id={self.id}, chat_id={self.chat_id}, message={self.message}, created_at={self.created_at}, is_read={self.is_read})>"

