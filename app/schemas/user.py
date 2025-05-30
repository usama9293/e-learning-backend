from pydantic import BaseModel, EmailStr
from datetime import date,time
from typing import Optional
import enum

class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"
    admin = "admin"

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: Optional[bool] = True

class StudentInfoCreate(BaseModel):
    full_name: str
    dob: str
    gender: str
    contact_number: str
    address: str
    grade_level: str = "None"
    emergency_contact: str = "None"
    parent_guardian: str = "None"

class StudentInfoOut(BaseModel):
    full_name: str
    dob: date
    gender: str
    contact_number: str
    address: str
    grade_level: str = "None"
    emergency_contact: str = "None"
    parent_guardian: str = "None"
class TutorInfoCreate(BaseModel):
    full_name: str
    dob: date
    gender: str
    contact_number: str
    address: str
    # Add more tutor-specific fields as needed

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    # Info fields (optional, validated in endpoint)
    full_name: str = None
    dob: str = None
    gender: str = None
    contact_number: str = None
    address: str = None
    grade_level: str = None
    emergency_contact: str = None
    parent_guardian: str = None

class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]

class UserInDB(UserBase):
    id: int
    hashed_password: str
    class Config:
        orm_mode = True

class UserOut(UserBase):
    id: int
    class Config:
     
        from_attributes = True  # or orm_mode = True for Pydantic v1
