from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class LogBase(BaseModel):
    timestamp: Optional[datetime]
    action: str
    user: str

class LogCreate(LogBase):
    pass

class LogUpdate(BaseModel):
    timestamp: Optional[datetime]
    action: Optional[str]
    user: Optional[str]

class LogInDB(LogBase):
    id: int
    class Config:
        orm_mode = True

class LogOut(LogBase):
    id: int
    class Config:
        orm_mode = True 