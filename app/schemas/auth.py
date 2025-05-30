from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    userId: int
    currentPassword: str
    newPassword: str
