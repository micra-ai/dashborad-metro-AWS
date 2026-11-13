from app.models.telemetry import ConstructionActivity
from app.services.telemetry_ingest import persist, utc_naive

NAMES = {"excavation": "Excavacion", "topography": "Topografia",
         "partial_seal": "Sello", "mesh_frames": "Malla y marcos", "hp1": "HP1",
         "shotcrete": "Shotcrete pendiente de clasificacion"}


def ingest_construction(payload, db):
    data = payload.object
    detected = data.stage_code
    classified = detected
    classification_status = "CLASSIFIED"
    if detected == "shotcrete":
        classified = {"sin_aplicar": "partial_seal", "aplicado": "hp1"}.get(data.estado_sello, "shotcrete")
        if data.estado_sello == "desconocido":
            classification_status = "PENDING"
    incoming = data.model_dump(mode="json")
    normalized = dict(incoming, stage_code=classified, stage_name=NAMES[classified],
                      detected_stage_code=detected, classification_status=classification_status)
    stored = payload.model_dump(mode="json")
    stored["received_object"] = incoming
    stored["object"] = normalized
    raw, duplicate = persist(
        db, namespace="construction", device_id=payload.devEUI, event_id=data.event_id,
        event_type=data.event_type, incoming=incoming, stored=stored,
        build_row=lambda raw_id: ConstructionActivity(
            raw_event_id=raw_id, device_id=payload.devEUI, cycle_id=data.cycle_id,
            detected_stage_code=detected, classified_stage_code=classified,
            classification_status=classification_status, estado_sello=data.estado_sello,
            started_at=utc_naive(data.inicio_evento), ended_at=utc_naive(data.fin_evento),
            duration_seconds=data.duration_seconds))
    return {"status": "success", "duplicate": duplicate, "event_id": data.event_id,
            "cycle_id": data.cycle_id, "event_type": data.event_type,
            "detected_stage_code": detected, "stage_code": classified,
            "stage_name": NAMES[classified], "classification_status": classification_status,
            "received_at": raw.received_at.isoformat() + "Z"}
