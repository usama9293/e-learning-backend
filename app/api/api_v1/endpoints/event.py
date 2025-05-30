from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.event import EventOut, EventCreate, EventUpdate
from app.models.event import Event
from app.api.api_v1.deps import get_db
from sqlalchemy import desc
from app.core.create_log import create_log
from app.api.api_v1.deps import get_current_user
from app.models.user import User
router = APIRouter()

@router.get("/events", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@router.get("/events/latest", response_model=List[EventOut])
def latest_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(desc(Event.created_at)).limit(3).all()


@router.post("/events", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    new_event = Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    create_log(db,"Event Created", current_user.email)
    return new_event

@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    create_log(db,"Event Updated", current_user.email)
    return event

@router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    create_log(db,"Event Deleted", current_user.email)
    return {"detail": "Event deleted"}

