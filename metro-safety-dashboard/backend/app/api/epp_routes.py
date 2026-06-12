from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.epp_schema import EppEventPayload
from app.integration_config.authorized_devices import AUTHORIZED_DEVICES
from app.integration_config.schema_versions import SUPPORTED_SCHEMA_VERSIONS
from app.repositories.event_repository import create_raw_event, create_epp_event
from app.normalizers.epp_normalizer import normalize_epp_event
from app.utils.image_helper import save_base64_image, save_uploaded_file

router = APIRouter(prefix="/api/epp", tags=["epp"])

@router.post("/events", status_code=status.HTTP_201_CREATED)
def ingest_epp_event(payload: EppEventPayload, db: Session = Depends(get_db)):
    if payload.device_id not in AUTHORIZED_DEVICES or AUTHORIZED_DEVICES[payload.device_id] != "EPP_CAMERA":
        raise HTTPException(status_code=403, detail="Unauthorized device")
    
    if payload.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise HTTPException(status_code=400, detail="Unsupported schema version")

    try:
        raw_event = create_raw_event(db, payload.model_dump(), "VALID")
        normalized_data = normalize_epp_event(payload)
        
        # Save base64 image if present
        if payload.image_base64:
            try:
                image_url = save_base64_image(payload.image_base64, payload.event_id)
                normalized_data["image_url"] = image_url
            except Exception as img_err:
                print(f"Error saving base64 image: {img_err}")
                
        create_epp_event(db, raw_event, normalized_data)
        return {"status": "success", "message": "Event processed successfully", "event_id": payload.event_id}
    except Exception as e:
        create_raw_event(db, payload.model_dump(), "ERROR", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/{event_id}/image", status_code=status.HTTP_200_OK)
def upload_event_image(event_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    from app.models.epp_event import EppEvent
    db_epp = db.query(EppEvent).filter(EppEvent.event_id == event_id).first()
    if not db_epp:
        raise HTTPException(status_code=404, detail="EPP Event not found")
        
    try:
        image_url = save_uploaded_file(file, event_id)
        db_epp.image_url = image_url
        db.commit()
        return {"status": "success", "message": "Image uploaded successfully", "image_url": image_url}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
