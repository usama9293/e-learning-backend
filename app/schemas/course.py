from pydantic import BaseModel,Field
from typing import Optional,List
from datetime import datetime,time  

from app.schemas.session import SessionOut,SessionStudentOut
class CourseBase(BaseModel):
    price:float
    name: str
    description: str
    image: str

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass
    
class CourseInDB(CourseBase):
    id: int
    class Config:
        from_attributes = True

class CourseOut(CourseBase):
    id: int
    enrolled:bool = False
    class Config:
        from_attributes = True 
class StudentOut(BaseModel):
    id:int
    full_name:str

class StudentCoureTutor(BaseModel):
    full_name:str 


class StudentCourseOut(CourseBase):
    id:int
    sessions:List[SessionStudentOut ] = Field(default=list)
   
    class Config:
        from_attributes = True
class TutorCourseOut(CourseBase):
    id:int
    enrolled:int
    students:List[StudentOut] = Field(default_factory=list)
    class Config:
        from_attributes = True