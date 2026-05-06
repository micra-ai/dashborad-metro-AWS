from datetime import datetime
from app.schemas.excavation_schema import ExcavationEventPayload

def normalize_excavation_event(payload: ExcavationEventPayload):
    return {
        "event_id": payload.event_id,
        "device_id": payload.device_id,
        "timestamp": datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00")),
        "site": payload.location.site,
        "area": payload.location.area,
        "zone": payload.location.zone,
        "large_rocks_detected": payload.risk_detection.large_rocks_detected,
        "large_rocks_count": payload.risk_detection.large_rocks_count,
        "landslide_detected": payload.risk_detection.landslide_detected,
        "landslide_count": payload.risk_detection.landslide_count,
        "movement_detected": payload.risk_detection.movement_detected,
        "risk_level": payload.risk_detection.risk_level,
        "confidence": payload.risk_detection.confidence,
        "alarm_triggered": payload.alarm.alarm_triggered,
        "alarm_type": payload.alarm.alarm_type,
        "alarm_level": payload.alarm.alarm_level,
        "trigger_reason": payload.alarm.trigger_reason,
        "activation_duration_seconds": payload.alarm.activation_duration_seconds
    }
