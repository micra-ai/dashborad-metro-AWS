import hmac
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.telemetry import SensorReading
from app.schemas.sensor_schema import ExteriorReading, InteriorReading
from app.services.telemetry_ingest import persist, utc_naive

router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])


def verify_sensor_token(authorization: Optional[str] = Header(None)):
    if not settings.SENSOR_INGEST_TOKEN:
        raise HTTPException(503, "Configure SENSOR_INGEST_TOKEN en el servidor")
    token = (authorization or "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(token.encode("utf-8"), settings.SENSOR_INGEST_TOKEN.encode("utf-8")):
        raise HTTPException(401, "Token invalido o ausente")


def ingest_reading(payload, location, db, response):
    configured = (settings.SENSOR_EXTERIOR_DEVICES if location == "exterior"
                  else settings.SENSOR_INTERIOR_DEVICES)
    allowed = {item.strip().upper() for item in configured.split(",") if item.strip()}
    if payload.device_id not in allowed:
        raise HTTPException(403, "Sensor no autorizado para esta ubicacion")
    incoming = payload.model_dump(mode="json")
    raw, duplicate = persist(
        db, namespace="sensor-" + location, device_id=payload.device_id,
        event_id=payload.event_id, event_type="SENSOR_" + location.upper(),
        incoming=incoming, stored=incoming,
        build_row=lambda raw_id: SensorReading(
            raw_event_id=raw_id, device_id=payload.device_id, location=location,
            measured_at=utc_naive(payload.measured_at), temperature_c=payload.temperature_c,
            co2_ppm=getattr(payload, "co2_ppm", None)))
    response.status_code = 200 if duplicate else 201
    return {"status": "success", "duplicate": duplicate, "event_id": payload.event_id,
            "received_at": raw.received_at.isoformat() + "Z"}


@router.post("/exterior", status_code=201, dependencies=[Depends(verify_sensor_token)])
def exterior(payload: ExteriorReading, response: Response, db: Session = Depends(get_db)):
    return ingest_reading(payload, "exterior", db, response)


@router.post("/interior", status_code=201, dependencies=[Depends(verify_sensor_token)])
def interior(payload: InteriorReading, response: Response, db: Session = Depends(get_db)):
    return ingest_reading(payload, "interior", db, response)


@router.get("/readings", dependencies=[Depends(verify_sensor_token)])
def readings(location: Optional[str] = Query(None, pattern="^(interior|exterior)$"),
             device_id: Optional[str] = None, limit: int = Query(100, ge=1, le=1000),
             db: Session = Depends(get_db)):
    query = db.query(SensorReading)
    if location:
        query = query.filter(SensorReading.location == location)
    if device_id:
        query = query.filter(SensorReading.device_id == device_id.strip().upper())
    rows = query.order_by(SensorReading.measured_at.desc(), SensorReading.id.desc()).limit(limit).all()
    return {"readings": [{"id": r.id, "device_id": r.device_id, "location": r.location,
                          "measured_at": r.measured_at.isoformat() + "Z",
                          "temperature_c": r.temperature_c, "co2_ppm": r.co2_ppm} for r in rows]}
