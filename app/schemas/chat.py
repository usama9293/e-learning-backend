from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List
class ChatMessageOut(BaseModel):
    id: int
    message: str
    created_at: datetime
    sender_id: int
    receiver_id: int

class ChatOut(BaseModel):
    id: int
    course_id: int
    student_id: int
    tutor_id: int
    chats:Optional[List[ChatMessageOut]] = None
    class Config:
        from_attributes = True
