from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import date, time
from app.schemas.tutor import TutorOut
class CourseOut(BaseModel):
    name: str
    description: str
    image: str
    enrolled:bool = False
    class Config:
        from_attributes = True 
class SessionBase(BaseModel):
    course_id: int
    tutor_info_id:int
    date: str
    days: list[str]
    start_time: str
    end_time: str
    status: Optional[str] = "scheduled"
    description: Optional[str] = "Description"
    title: Optional[str] = "Title"

class SessionCreate(SessionBase):
    pass

class SessionUpdate(SessionBase):
    pass
    # date: Optional[str]
    # time: Optional[str]
    # status: Optional[str]

class SessionInDB(SessionBase):
    id: int
    class Config:
        orm_mode = True

class TutorInfoOut(BaseModel):
    full_name: str
   

class StudentOut(BaseModel):
    id:int
    full_name:str

class SessionStudentOut(BaseModel):
    id: int
    date: date
    days: list[str]
    start_time: time
    end_time: time
    status: str
    description: str
    title: str
    course: CourseOut
    full_name:str
    tutor: TutorInfoOut
    class Config:
        from_attributes = True
    
class SessionOut(BaseModel):
    id: int
    course_id: int
    tutor_info_id: int
    date: date
    days: list[str]
    start_time: time
    end_time: time
    status: str
    description: str
    title: str
    course: CourseOut
    full_name:str
    students: List[StudentOut] = Field(default_factory=list)
    # tutor: TutorInfoOut
    class Config:
        from_attributes = True