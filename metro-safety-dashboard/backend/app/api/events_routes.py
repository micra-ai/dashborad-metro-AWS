from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.models.raw_event import RawEvent
from app.auth.routes import get_current_user

router = APIRouter(prefix="/api/events", tags=["events"], dependencies=[Depends(get_current_user)])

@router.get("")
def get_events(
    event_type: Optional[str] = None,
    device_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(RawEvent)
    if event_type:
        query = query.filter(RawEvent.event_type == event_type)
    if device_id:
        query = query.filter(RawEvent.device_id == device_id)
    if start_date:
        query = query.filter(RawEvent.received_at >= start_date)
    if end_date:
        query = query.filter(RawEvent.received_at <= end_date)
    
    events = query.order_by(RawEvent.received_at.desc()).offset(offset).limit(limit).all()
    return events
