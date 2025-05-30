from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, default="Maths Mastery Institute")
    site_description = Column(String, default="Maths Mastery Institute")
    contact_email = Column(String, default="admin@example.com")
    maintenance_mode = Column(Boolean, default=False)
    max_file_size = Column(Integer, default=10)
    allowed_file_types = Column(String, default="jpg,png,pdf")
    session_timeout = Column(Integer, default=30)
    max_login_attempts = Column(Integer, default=5)
    enable_registration = Column(Boolean, default=True)
    enable_email_verification = Column(Boolean, default=True)
    default_user_role = Column(String, default="student")
    payment_gateway = Column(String, default="stripe")
    currency = Column(String, default="USD")
