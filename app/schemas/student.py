from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    address:str 
    gender:str 
    emergency_contact:str
    is_active: bool = True

class StudentCreate(StudentBase):
    password: str = Field(..., min_length=8)
    role: str = "student"

class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

class StudentOut(StudentBase):
    id: int
    # role: str
    # created_at: datetime
    # updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
