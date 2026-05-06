from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.excavation_schema import ExcavationEventPayload
from app.integration_config.authorized_devices import AUTHORIZED_DEVICES
from app.integration_config.schema_versions import SUPPORTED_SCHEMA_VERSIONS
from app.repositories.event_repository import create_raw_event, create_excavation_event
from app.normalizers.excavation_normalizer import normalize_excavation_event

router = APIRouter(prefix="/api/excavation", tags=["excavation"])

@router.post("/events", status_code=status.HTTP_201_CREATED)
def ingest_excavation_event(payload: ExcavationEventPayload, db: Session = Depends(get_db)):
    if payload.device_id not in AUTHORIZED_DEVICES or AUTHORIZED_DEVICES[payload.device_id] != "EXCAVATION_CAMERA":
        raise HTTPException(status_code=403, detail="Unauthorized device")
    
    if payload.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise HTTPException(status_code=400, detail="Unsupported schema version")

    try:
        raw_event = create_raw_event(db, payload.model_dump(), "VALID")
        normalized_data = normalize_excavation_event(payload)
        create_excavation_event(db, raw_event, normalized_data)
        return {"status": "success", "message": "Event processed successfully", "event_id": payload.event_id}
    except Exception as e:
        create_raw_event(db, payload.model_dump(), "ERROR", str(e))
        raise HTTPException(status_code=500, detail=str(e))
