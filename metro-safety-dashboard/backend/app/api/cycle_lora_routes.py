import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.milesight_routes import verify_milesight_token
from app.database.session import get_db
from app.integration_config.authorized_devices import AUTHORIZED_DEVICES
from app.models.raw_event import RawEvent
from app.models.cycle_event import CycleStage, ExcavationCycle
from app.schemas.cycle_lora_schema import CycleLoRaUplinkPayload


router = APIRouter(tags=["excavation-cycle-lorawan"])


def _event_time(payload):
    return datetime.utcfromtimestamp(payload.timestamp) if payload.timestamp else datetime.utcnow()


def _require_stage(data):
    if not data.stage_code or not data.stage_name or data.sequence is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Los eventos de hito requieren stage_code, stage_name y sequence",
        )


def process_cycle_lora_payload(payload: CycleLoRaUplinkPayload, db: Session):
    payload.devEUI = payload.devEUI.strip().upper()
    if payload.devEUI not in AUTHORIZED_DEVICES:
        raise HTTPException(status_code=403, detail=f"Dispositivo no autorizado: {payload.devEUI}")

    data = payload.object
    event_at = _event_time(payload)
    received_at = datetime.utcnow()
    raw = RawEvent(
        event_id="lora_" + uuid.uuid4().hex,
        event_type=data.event_type,
        schema_version="4.0",
        device_id=payload.devEUI,
        received_at=received_at,
        raw_payload=json.dumps(payload.model_dump(), ensure_ascii=False),
        validation_status="VALID",
    )
    db.add(raw)
    if data.event_type in ("HEARTBEAT_STATUS", "STAGE_START", "STAGE_END"):

        if data.event_type in ("STAGE_START", "STAGE_END") and not data.stage_code:

            raise HTTPException(status_code=422, detail="La actividad requiere stage_code")
        db.commit()
        return {"status": "success", "event_type": data.event_type,
                "received_at": received_at.isoformat() + "Z"}
    cycle = db.query(ExcavationCycle).filter(ExcavationCycle.cycle_id == data.cycle_id).first()

    if data.event_type == "CYCLE_START":
        if not cycle:
            cycle = ExcavationCycle(
                cycle_id=data.cycle_id,
                device_id=payload.devEUI,
                front=data.front,
                shift=data.shift,
                started_at=event_at,
                target_duration_seconds=data.cycle_target_duration_seconds,
                status="IN_PROGRESS",
            )
            db.add(cycle)
            db.commit()
            db.refresh(cycle)

    else:
        if not cycle:
            raise HTTPException(status_code=404, detail="Ciclo no encontrado; envíe CYCLE_START primero")

        if data.event_type in ("STAGE_START", "STAGE_END"):
            _require_stage(data)
            stage = (
                db.query(CycleStage)
                .filter(CycleStage.cycle_id == cycle.id, CycleStage.stage_code == data.stage_code)
                .order_by(CycleStage.id.desc())
                .first()
            )
            if data.event_type == "STAGE_START" and not stage:
                stage = CycleStage(
                    cycle_id=cycle.id,
                    stage_code=data.stage_code,
                    stage_name=data.stage_name,
                    sequence=data.sequence,
                    started_at=event_at,
                    target_duration_seconds=data.target_duration_seconds,
                    confidence=data.confidence,
                    evidence_url=data.evidence_url,
                    tracked_object=data.tracked_object,
                    visible_seconds=data.visible_seconds,
                    status="IN_PROGRESS",
                )
                db.add(stage)
            elif data.event_type == "STAGE_END":
                if not stage:
                    started_at = event_at - timedelta(seconds=data.duration_seconds or 0)
                    stage = CycleStage(
                        cycle_id=cycle.id,
                        stage_code=data.stage_code,
                        stage_name=data.stage_name,
                        sequence=data.sequence,
                        started_at=started_at,
                        target_duration_seconds=data.target_duration_seconds,
                    )
                    db.add(stage)
                if data.duration_seconds is not None:

                    stage.started_at = event_at - timedelta(seconds=data.duration_seconds)

                stage.ended_at = event_at

                stage.confidence = data.confidence
                stage.evidence_url = data.evidence_url or stage.evidence_url
                stage.tracked_object = data.tracked_object or stage.tracked_object
                stage.visible_seconds = data.visible_seconds
                stage.status = "COMPLETED"

        elif data.event_type == "CYCLE_END":
            cycle.ended_at = event_at
            cycle.advance_meters = data.advance_meters
            cycle.status = "COMPLETED"

        db.commit()

    db.commit()
    return {
        "status": "success",
        "message": "Evento del ciclo de excavación recibido por LoRaWAN",
        "cycle_id": data.cycle_id,
        "event_type": data.event_type,
        "stage_code": data.stage_code,
        "received_at": event_at.isoformat(),
        "radio": {"devEUI": payload.devEUI, "rssi": payload.rssi, "snr": payload.snr},
    }


@router.post(
    "/api/v1/lorawan/linea9-cycle",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_milesight_token)],
)
def receive_cycle_event(payload: CycleLoRaUplinkPayload, db: Session = Depends(get_db)):
    return process_cycle_lora_payload(payload, db)


@router.get("/api/v1/lorawan/linea9-status")
def lora_status(db: Session = Depends(get_db)):
    rows = (db.query(RawEvent)
            .filter(RawEvent.schema_version == "4.0",
                    RawEvent.device_id.in_(list(AUTHORIZED_DEVICES)))
            .order_by(RawEvent.received_at.desc(), RawEvent.id.desc()).limit(20).all())
    events = []
    for row in rows:
        payload = json.loads(row.raw_payload)
        events.append({"id": row.id, "received_at": row.received_at.isoformat() + "Z",
                       "device_id": row.device_id, "event_type": row.event_type,
                       "object": payload.get("object", {}),
                       "rssi": payload.get("rssi"), "snr": payload.get("snr")})
    heartbeat = (db.query(RawEvent)
                 .filter(RawEvent.schema_version == "4.0",
                         RawEvent.device_id.in_(list(AUTHORIZED_DEVICES)),
                         RawEvent.event_type == "HEARTBEAT_STATUS")
                 .order_by(RawEvent.received_at.desc(), RawEvent.id.desc()).first())
    camera = None
    if heartbeat:
        camera = {"received_at": heartbeat.received_at.isoformat() + "Z",
                  "device_id": heartbeat.device_id,
                  **json.loads(heartbeat.raw_payload).get("object", {})}
    return {"generated_at": datetime.utcnow().isoformat() + "Z",
            "latest_event": events[0] if events else None,
            "heartbeat": camera, "recent_events": events}




# ACTIVITIES_DAY_V1

@router.get("/api/v1/lorawan/linea9-activities-day")

def activity_day(day: str, db: Session = Depends(get_db)):

    from datetime import datetime as DT, timedelta as TD, timezone as TZ

    from zoneinfo import ZoneInfo



    try:

        local_day = DT.strptime(day, "%Y-%m-%d")

    except ValueError:

        raise HTTPException(status_code=422, detail="Use fecha YYYY-MM-DD")



    chile = ZoneInfo("America/Santiago")

    start = local_day.replace(tzinfo=chile)

    end = (local_day + TD(days=1)).replace(tzinfo=chile)

    start_utc = start.astimezone(TZ.utc).replace(tzinfo=None)

    end_utc = end.astimezone(TZ.utc).replace(tzinfo=None)



    rows = (

        db.query(RawEvent)

        .filter(

            RawEvent.schema_version == "4.0",

            RawEvent.device_id.in_(list(AUTHORIZED_DEVICES)),

            RawEvent.event_type.in_(("HEARTBEAT_STATUS", "STAGE_START", "STAGE_END")),

            RawEvent.received_at >= start_utc,

            RawEvent.received_at < end_utc,

        )

        .order_by(RawEvent.received_at.asc(), RawEvent.id.asc())

        .all()

    )

    events = []

    for row in rows:

        try:

            payload = json.loads(row.raw_payload)

            obj = payload.get("object") or {}

            if not isinstance(obj, dict):

                continue

        except (ValueError, TypeError, AttributeError):

            continue

        events.append({

            "id": row.id,

            "device_id": row.device_id,
            "event_type": row.event_type,

            "received_at": row.received_at.isoformat() + "Z",

            "object": obj,

        })



    return {

        "day": day,

        "timezone": "America/Santiago",

        "generated_at": DT.now(TZ.utc).isoformat(),

        "events": events,

    }

