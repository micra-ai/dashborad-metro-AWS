from datetime import datetime
from app.schemas.epp_schema import EppEventPayload

def normalize_epp_event(payload: EppEventPayload):
    return {
        "event_id": payload.event_id,
        "device_id": payload.device_id,
        "timestamp": datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00")),
        "site": payload.location.site,
        "area": payload.location.area,
        "zone": payload.location.zone,
        "workers_detected": payload.summary.workers_detected,
        "workers_full_compliance": payload.summary.workers_full_compliance,
        "workers_partial_compliance": payload.summary.workers_partial_compliance,
        "workers_without_required_ppe": payload.summary.workers_without_required_ppe,
        "overall_compliance_percentage": payload.summary.overall_compliance_percentage,
        "missing_helmet_count": sum(1 for w in payload.workers if "helmet" in w.missing_ppe),
        "missing_gloves_count": sum(1 for w in payload.workers if "gloves" in w.missing_ppe),
        "missing_goggles_count": sum(1 for w in payload.workers if "goggles" in w.missing_ppe),
        "missing_reflective_vest_count": sum(1 for w in payload.workers if "reflective_vest" in w.missing_ppe),
        "missing_mask_count": sum(1 for w in payload.workers if "mask" in w.missing_ppe),
        "alert_level": payload.alerts.alert_level,
        "non_compliance_detected": payload.alerts.non_compliance_detected
    }
