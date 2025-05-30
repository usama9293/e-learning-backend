from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ... existing schemas ...

class TutorCourseBase(BaseModel):
    tutor_id: int
    course_id: int

class TutorCourseCreate(TutorCourseBase):
    pass

class TutorCourseResponse(TutorCourseBase):
    id: int
    assigned_date: datetime

    class Config:
        from_attributes = True

class TutorCourseWithDetails(TutorCourseResponse):
    tutor: dict  # Will contain tutor details
    course: dict  # Will contain course details

    class Config:
        from_attributes = True

# Update CourseResponse to include tutor information
class CourseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    schedule_date: str
    schedule_time: str
    created_at: datetime
    tutors: List[dict] = []  # List of tutor details

    class Config:
        from_attributes = True

# Update UserResponse to include assigned courses for tutors
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    assigned_courses: List[dict] = []  # List of course details for tutors
    enrolled_courses: List[dict] = []  # List of course details for students

    class Config:
        from_attributes = True 