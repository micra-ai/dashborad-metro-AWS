from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.epp_event import EppEvent
from app.models.excavation_event import ExcavationEvent
from app.models.raw_event import RawEvent
from app.schemas.dashboard_schema import DashboardSummary, EppSummary, ExcavationSummary
from datetime import datetime, timezone

def get_dashboard_summary(db: Session):
    total_events = db.query(RawEvent).count()
    last_event = db.query(RawEvent).order_by(RawEvent.received_at.desc()).first()
    last_update = last_event.received_at.isoformat() if last_event else datetime.now(timezone.utc).isoformat()
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

    total_positive = db.query(func.sum(EppEvent.positive_compliance_count)).scalar() or 0
    total_negative = db.query(func.sum(EppEvent.negative_compliance_count)).scalar() or 0

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
        positive_compliance_count=total_positive,
        negative_compliance_count=total_negative,
        most_frequent_missing_ppe=most_frequent if most_frequent and missing_ppe_counts[most_frequent] > 0 else None
    )

def get_excavation_summary(db: Session):
    last_event = db.query(ExcavationEvent).order_by(ExcavationEvent.timestamp.desc()).first()
    
    device_status = "Offline"
    last_seen = None
    rocas = 0
    deslizamientos = 0
    avance = 0.0

    if last_event:
        last_seen = last_event.timestamp.isoformat() if last_event.timestamp else None
        rocas = getattr(last_event, "large_rocks_count", 0) or 0
        deslizamientos = getattr(last_event, "landslide_count", 0) or 0
        avance = getattr(last_event, "avance_metros", 0.0) or 0.0

        if last_event.timestamp:
            ts = last_event.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            seconds_diff = (now - ts).total_seconds()
            if 0 <= seconds_diff <= 900:  # 15 minutes = 900 seconds
                device_status = "Online"

    total_rocks = db.query(ExcavationEvent).filter(ExcavationEvent.large_rocks_detected == True).count()
    total_landslides = db.query(ExcavationEvent).filter(ExcavationEvent.landslide_detected == True).count()
    total_alarms = db.query(ExcavationEvent).filter(ExcavationEvent.alarm_triggered == True).count()
    current_risk = last_event.risk_level if last_event else "LOW"

    return ExcavationSummary(
        rocas_detectadas=rocas,
        deslizamientos=deslizamientos,
        avance_metros=avance,
        device_status=device_status,
        last_seen=last_seen,
        total_large_rocks_detections=total_rocks,
        total_landslide_detections=total_landslides,
        current_risk_level=current_risk,
        total_alarms_triggered=total_alarms
    )

def get_latest_images(db: Session, limit: int = 5):
    compliant = db.query(EppEvent).filter(
        EppEvent.image_url.isnot(None),
        EppEvent.image_url != "",
        EppEvent.non_compliance_detected == False
    ).order_by(EppEvent.timestamp.desc()).limit(limit).all()

    non_compliant = db.query(EppEvent).filter(
        EppEvent.image_url.isnot(None),
        EppEvent.image_url != "",
        EppEvent.non_compliance_detected == True
    ).order_by(EppEvent.timestamp.desc()).limit(limit).all()

    return {
        "compliant": [
            {
                "event_id": ev.event_id,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                "site": ev.site,
                "area": ev.area,
                "zone": ev.zone,
                "image_url": ev.image_url,
                "workers_detected": ev.workers_detected,
                "workers_full_compliance": ev.workers_full_compliance,
                "overall_compliance_percentage": ev.overall_compliance_percentage
            }
            for ev in compliant
        ],
        "non_compliant": [
            {
                "event_id": ev.event_id,
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else None,
                "site": ev.site,
                "area": ev.area,
                "zone": ev.zone,
                "image_url": ev.image_url,
                "workers_detected": ev.workers_detected,
                "workers_full_compliance": ev.workers_full_compliance,
                "overall_compliance_percentage": ev.overall_compliance_percentage,
                "missing_helmet_count": ev.missing_helmet_count,
                "missing_gloves_count": ev.missing_gloves_count,
                "missing_goggles_count": ev.missing_goggles_count,
                "missing_reflective_vest_count": ev.missing_reflective_vest_count,
                "missing_mask_count": ev.missing_mask_count
            }
            for ev in non_compliant
        ]
    }
