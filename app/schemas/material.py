from pydantic import BaseModel,Field
from typing import Optional
from typing import List
from datetime import datetime
class MaterialBase(BaseModel):
    session_id: int
    name: str
    description:str
    link:str 
    file_path:str

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str]
    file_path: Optional[str]

class MaterialInDB(MaterialBase):
    id: int
    class Config:
        orm_mode = True

class MaterialOut(MaterialBase):
    id: int
    created_at:datetime
    
    class Config:
        from_attributes  = True