from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class TutorBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    is_active: bool = True
    specialization: str = Field(..., min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

class TutorCreate(TutorBase):
    password: str = Field(..., min_length=8)
    role: str = "tutor"

class TutorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    specialization: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class TutorOut(TutorBase):
    id: int
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    courses: List[int] = []  # List of course IDs

    class Config:
        from_attributes = True 