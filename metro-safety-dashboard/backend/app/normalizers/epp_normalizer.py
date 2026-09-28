from datetime import datetime
from app.schemas.epp_schema import EppEventPayload

def normalize_epp_event(payload: EppEventPayload):
    pos_count = 0
    neg_count = 0
    partial_count = 0
    compliance_sum = 0

    for w in payload.workers:
        has_helmet = (
            w.ppe.helmet is not None
            and w.ppe.helmet.detected
        )

        has_vest = (
            w.ppe.reflective_vest is not None
            and w.ppe.reflective_vest.detected
        )

        # Línea 9: EPP requerido = casco + chaleco reflectante
        worker_compliance = (
            (50 if has_helmet else 0) +
            (50 if has_vest else 0)
        )

        compliance_sum += worker_compliance

        if worker_compliance == 100:
            pos_count += 1
        elif worker_compliance == 50:
            partial_count += 1
            neg_count += 1
        else:
            neg_count += 1

    workers_detected = len(payload.workers)

    overall_compliance_percentage = (
        round(compliance_sum / workers_detected, 2)
        if workers_detected > 0
        else 0
    )

    non_compliance_detected = (
        workers_detected > 0
        and overall_compliance_percentage < 100
    )

    return {
        "event_id": payload.event_id,
        "device_id": payload.device_id,
        "timestamp": datetime.fromisoformat(
            payload.timestamp.replace("Z", "+00:00")
        ),
        "site": payload.location.site,
        "area": payload.location.area,
        "zone": payload.location.zone,

        "workers_detected": workers_detected,
        "workers_full_compliance": pos_count,
        "workers_partial_compliance": partial_count,
        "workers_without_required_ppe": sum(
            1
            for w in payload.workers
            if not (
                w.ppe.helmet is not None
                and w.ppe.helmet.detected
            )
            and not (
                w.ppe.reflective_vest is not None
                and w.ppe.reflective_vest.detected
            )
        ),

        "overall_compliance_percentage": overall_compliance_percentage,

        "missing_helmet_count": sum(
            1
            for w in payload.workers
            if not (
                w.ppe.helmet is not None
                and w.ppe.helmet.detected
            )
        ),

        "missing_gloves_count": 0,
        "missing_goggles_count": 0,

        "missing_reflective_vest_count": sum(
            1
            for w in payload.workers
            if not (
                w.ppe.reflective_vest is not None
                and w.ppe.reflective_vest.detected
            )
        ),

        "missing_mask_count": 0,

        "alert_level": payload.alerts.alert_level,
        "non_compliance_detected": non_compliance_detected,

        "positive_compliance_count": pos_count,
        "negative_compliance_count": neg_count
    }
