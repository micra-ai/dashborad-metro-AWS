from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.milesight_schema import MilesightUplinkPayload
from app.api.milesight_routes import verify_milesight_token, process_milesight_payload

router = APIRouter(prefix="/api/excavation", tags=["excavation"])

@router.post("/events", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_milesight_token)])
def ingest_excavation_event(payload: MilesightUplinkPayload, db: Session = Depends(get_db)):
    try:
        return process_milesight_payload(payload, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar telemetria: {str(e)}"
        )
