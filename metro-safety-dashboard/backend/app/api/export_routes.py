from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io
from app.database.session import get_db
from app.models.raw_event import RawEvent
from app.auth.routes import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"], dependencies=[Depends(get_current_user)])

@router.get("/csv")
def export_csv(
    event_type: Optional[str] = None,
    device_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
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
    
    events = query.order_by(RawEvent.received_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "event_id", "event_type", "device_id", "received_at", "validation_status"])
    for event in events:
        writer.writerow([event.id, event.event_id, event.event_type, event.device_id, event.received_at.isoformat(), event.validation_status])
        
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=events.csv"
    return response
