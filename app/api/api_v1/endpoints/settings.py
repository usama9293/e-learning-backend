from fastapi import APIRouter, Depends, HTTPException
from app.schemas.settings import SystemSettings
from app.models.settings import SystemSettings as SystemSettingsModel
from app.api.api_v1.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/admin/settings", response_model=SystemSettings)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSettingsModel).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


    # Example hardcoded response (you'd typically fetch from DB or config file)
    return {
        "site_name": "My Site",
        "site_description": "A brief description of the site.",
        "contact_email": "admin@example.com",
        "maintenance_mode": False,
        "max_file_size": 5,
        "allowed_file_types": "jpg,png,pdf",
        "session_timeout": 30,
        "max_login_attempts": 5,
        "enable_registration": True,
        "enable_email_verification": True,
        "default_user_role": "student",
        "payment_gateway": "stripe",
        "currency": "USD",
    }
@router.put("/admin/settings")
def update_settings(settings: SystemSettings):
    # Save settings to DB or configuration file
    # Example: db.save_settings(settings.dict())
    return {"message": "Settings updated successfully"}
