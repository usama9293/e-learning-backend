from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    due_date: datetime
    total_points: float = Field(..., gt=0)
    session_id: int

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    due_date: Optional[datetime] = None
    total_points: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None

class AssignmentOut(AssignmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    # submissions_count: int = 0

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    assignment_id: int
    content: str = Field(..., min_length=1)
    file_url: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    file_url: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None

class SubmissionOut(SubmissionBase):
    id: int
    student_id: int
    grade: Optional[float] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True 