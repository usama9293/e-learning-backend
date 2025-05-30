from pydantic import BaseModel, EmailStr
from typing import Optional

class SystemSettings(BaseModel):
    site_name: str
    site_description: str
    contact_email: EmailStr
    maintenance_mode: bool
    max_file_size: int
    allowed_file_types: str
    session_timeout: int
    max_login_attempts: int
    enable_registration: bool
    enable_email_verification: bool
    default_user_role: str
    payment_gateway: str
    currency: str
