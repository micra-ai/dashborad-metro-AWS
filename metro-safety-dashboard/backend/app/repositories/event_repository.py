from sqlalchemy.orm import Session
from app.models.raw_event import RawEvent
from app.models.epp_event import EppEvent
from app.models.excavation_event import ExcavationEvent
import json

def create_raw_event(db: Session, payload: dict, validation_status: str, validation_errors: str = None):
    db_raw_event = RawEvent(
        event_id=payload.get("event_id"),
        event_type=payload.get("event_type"),
        schema_version=payload.get("schema_version"),
        device_id=payload.get("device_id"),
        raw_payload=json.dumps(payload),
        validation_status=validation_status,
        validation_errors=validation_errors
    )
    db.add(db_raw_event)
    db.commit()
    db.refresh(db_raw_event)
    return db_raw_event

def create_epp_event(db: Session, db_raw_event: RawEvent, data: dict):
    db_epp = EppEvent(
        raw_event_id=db_raw_event.id,
        **data
    )
    db.add(db_epp)
    db.commit()
    db.refresh(db_epp)
    return db_epp

def create_excavation_event(db: Session, db_raw_event: RawEvent, data: dict):
    db_excavation = ExcavationEvent(
        raw_event_id=db_raw_event.id,
        **data
    )
    db.add(db_excavation)
    db.commit()
    db.refresh(db_excavation)
    return db_excavation
