from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class EventBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str]
    image: Optional[str]

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str]
    date: Optional[datetime]
    description: Optional[str]
    image:Optional[str]

class EventInDB(EventBase):
    id: int
    class Config:
        orm_mode = True

class EventOut(EventBase):
    id: int
    class Config:
        orm_mode = True 