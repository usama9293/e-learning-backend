from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.db.base import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    date = Column(Date)
    status = Column(String)
