from pydantic import BaseModel, EmailStr, conint, constr
from typing import Literal

class SystemSettings(BaseModel):
    site_name: str
    site_description: str
    contact_email: EmailStr
    maintenance_mode: bool
    max_file_size: conint(ge=1)  # must be >= 1 MB
    allowed_file_types: str  # Comma-separated list like 'jpg,png,pdf'
    session_timeout: conint(ge=1)  # in minutes
    max_login_attempts: conint(ge=1)
    enable_registration: bool
    enable_email_verification: bool
    default_user_role: Literal["student", "tutor"]
    payment_gateway: Literal["stripe", "paypal"]
    currency: Literal["USD", "EUR", "GBP"]
