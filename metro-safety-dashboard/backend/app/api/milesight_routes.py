from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
import datetime
import time

from app.database.session import get_db
from app.schemas.milesight_schema import MilesightUplinkPayload
from app.integration_config.authorized_devices import AUTHORIZED_DEVICES
from app.repositories.event_repository import create_raw_event, create_excavation_event

router = APIRouter(tags=["milesight-lorawan"])

TOKEN_SECRETO = "EBR_Metro_Secret_Token_2026"

def verify_milesight_token(
    authorization: Optional[str] = Header(None),
    x_milesight_token: Optional[str] = Header(None)
):
    token = None
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1].strip()
        else:
            token = authorization.strip()
    elif x_milesight_token:
        token = x_milesight_token.strip()

    if TOKEN_SECRETO and token != TOKEN_SECRETO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorizacion invalido o ausente"
        )

def process_milesight_payload(payload: MilesightUplinkPayload, db: Session):
    # 1. Device Authorization Check
    if payload.devEUI not in AUTHORIZED_DEVICES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Dispositivo no autorizado: {payload.devEUI}"
        )

    # 2. Extract telemetry from object or fallback hex string
    if payload.object:
        rocas = payload.object.rocas_detectadas
        desliza = payload.object.deslizamientos
        avance_m = payload.object.avance_metros
    elif payload.data and len(payload.data) >= 8:
        try:
            bytes_data = bytes.fromhex(payload.data[:8])
            rocas = bytes_data[0]
            desliza = bytes_data[1]
            avance_m = ((bytes_data[2] << 8) | bytes_data[3]) / 100.0
        except Exception as hex_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error decodificando payload hexadecimal 'data': {str(hex_err)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se recibio la clave 'object' decodificada ni un payload 'data' hexadecimal valido."
        )

    # 3. Create Raw Event
    import uuid
    event_id = f"milesight_{payload.devEUI}_{payload.timestamp or int(time.time())}_{payload.fCnt or 0}_{uuid.uuid4().hex[:6]}"
    raw_payload_dict = payload.model_dump()
    raw_payload_dict["event_id"] = event_id
    raw_payload_dict["event_type"] = "EXCAVATION_LORAWAN"
    raw_payload_dict["schema_version"] = "1.0.0"
    raw_payload_dict["device_id"] = payload.devEUI

    raw_event = create_raw_event(db, raw_payload_dict, "VALID")

    # 4. Map into Excavation Event table
    from datetime import timezone
    event_dt = datetime.datetime.fromtimestamp(payload.timestamp, tz=timezone.utc) if payload.timestamp else datetime.datetime.now(timezone.utc)
    
    normalized_data = {
        "event_id": event_id,
        "device_id": payload.devEUI,
        "timestamp": event_dt,
        "site": payload.applicationName or "Metro Pique 1",
        "area": payload.deviceName or "Excavation Zone",
        "zone": "Pique 1",
        "large_rocks_detected": rocas > 0,
        "large_rocks_count": rocas,
        "landslide_detected": desliza > 0,
        "landslide_count": desliza,
        "movement_detected": (rocas > 0 or desliza > 0 or avance_m > 0),
        "avance_metros": avance_m,
        "risk_level": "HIGH" if desliza > 0 else ("MEDIUM" if rocas > 0 else "LOW"),
        "confidence": 1.0,
        "alarm_triggered": desliza > 0,
        "alarm_type": "LANDSLIDE_ALERT" if desliza > 0 else None,
        "alarm_level": "CRITICAL" if desliza > 0 else None,
        "trigger_reason": "Deslizamiento detectado por UG65" if desliza > 0 else None,
        "activation_duration_seconds": 30 if desliza > 0 else 0
    }

    create_excavation_event(db, raw_event, normalized_data)

    return {
        "status": "success",
        "message": "Telemetria procesada exitosamente",
        "received_data": {
            "devEUI": payload.devEUI,
            "rocas_detectadas": rocas,
            "deslizamientos": desliza,
            "avance_metros": avance_m,
            "rssi": payload.rssi,
            "snr": payload.snr
        }
    }

@router.post("/api/v1/lorawan/milesight-ug65", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_milesight_token)])
def receive_milesight_telemetry(payload: MilesightUplinkPayload, db: Session = Depends(get_db)):
    try:
        return process_milesight_payload(payload, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar telemetria: {str(e)}"
        )
