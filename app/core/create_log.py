from app.models.log import Log
from sqlalchemy.orm import Session
from datetime import datetime

def create_log(db: Session, action: str, user_email: str):
    log = Log(
        timestamp=datetime.utcnow(),
        action=action,
        user=user_email
    )
    db.add(log)
    db.commit()
