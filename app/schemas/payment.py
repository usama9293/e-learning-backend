from pydantic import BaseModel
from typing import Optional

class PaymentBase(BaseModel):
    user_id: int
    amount: float
    date: Optional[str]
    status: Optional[str]

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float]
    date: Optional[str]
    status: Optional[str]

class PaymentInDB(PaymentBase):
    id: int
    class Config:
        orm_mode = True

class PaymentOut(PaymentBase):
    id: int
    class Config:
        orm_mode = True 