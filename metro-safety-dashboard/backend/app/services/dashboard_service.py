from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.epp_event import EppEvent
from app.models.excavation_event import ExcavationEvent
from app.models.raw_event import RawEvent
from app.schemas.dashboard_schema import DashboardSummary, EppSummary, ExcavationSummary
from datetime import datetime

def get_dashboard_summary(db: Session):
    total_events = db.query(RawEvent).count()
    last_event = db.query(RawEvent).order_by(RawEvent.received_at.desc()).first()
    last_update = last_event.received_at.isoformat() if last_event else datetime.utcnow().isoformat()
    active_devices = db.query(RawEvent.device_id).distinct().count()
    return DashboardSummary(
        total_events=total_events,
        last_update=last_update,
        active_devices_count=active_devices
    )

def get_epp_summary(db: Session):
    total_workers = db.query(func.sum(EppEvent.workers_detected)).scalar() or 0
    total_full = db.query(func.sum(EppEvent.workers_full_compliance)).scalar() or 0
    total_partial = db.query(func.sum(EppEvent.workers_partial_compliance)).scalar() or 0
    avg_compliance = db.query(func.avg(EppEvent.overall_compliance_percentage)).scalar() or 0.0

    missing_ppe_counts = {
        "helmet": db.query(func.sum(EppEvent.missing_helmet_count)).scalar() or 0,
        "gloves": db.query(func.sum(EppEvent.missing_gloves_count)).scalar() or 0,
        "goggles": db.query(func.sum(EppEvent.missing_goggles_count)).scalar() or 0,
        "reflective_vest": db.query(func.sum(EppEvent.missing_reflective_vest_count)).scalar() or 0,
        "mask": db.query(func.sum(EppEvent.missing_mask_count)).scalar() or 0,
    }
    most_frequent = max(missing_ppe_counts, key=missing_ppe_counts.get) if total_workers > 0 else None

    return EppSummary(
        total_workers_detected=total_workers,
        overall_compliance_percentage=avg_compliance,
        workers_full_compliance=total_full,
        workers_partial_compliance=total_partial,
        most_frequent_missing_ppe=most_frequent if most_frequent and missing_ppe_counts[most_frequent] > 0 else None
    )

def get_excavation_summary(db: Session):
    total_rocks = db.query(ExcavationEvent).filter(ExcavationEvent.large_rocks_detected == True).count()
    total_landslides = db.query(ExcavationEvent).filter(ExcavationEvent.landslide_detected == True).count()
    total_alarms = db.query(ExcavationEvent).filter(ExcavationEvent.alarm_triggered == True).count()
    last_event = db.query(ExcavationEvent).order_by(ExcavationEvent.timestamp.desc()).first()
    current_risk = last_event.risk_level if last_event else "LOW"

    return ExcavationSummary(
        total_large_rocks_detections=total_rocks,
        total_landslide_detections=total_landslides,
        current_risk_level=current_risk,
        total_alarms_triggered=total_alarms
    )
