from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.cycle_event import ExcavationCycle, CycleStage
from app.schemas.cycle_schema import CycleCreate, StageCreate

router = APIRouter(prefix="/api/cycles", tags=["excavation-cycle"])


def _iso(value):
    return value.isoformat() if value else None


def _duration(started_at, ended_at):
    if not started_at:
        return 0
    end = ended_at or datetime.utcnow()
    return max(0, int((end - started_at).total_seconds()))


def _stage_payload(stage):
    duration = _duration(stage.started_at, stage.ended_at)
    return {
        "id": stage.id,
        "stage_code": stage.stage_code,
        "stage_name": stage.stage_name,
        "sequence": stage.sequence,
        "started_at": _iso(stage.started_at),
        "ended_at": _iso(stage.ended_at),
        "duration_seconds": duration,
        "target_duration_seconds": stage.target_duration_seconds,
        "deviation_seconds": duration - stage.target_duration_seconds,
        "confidence": stage.confidence,
        "evidence_url": stage.evidence_url,
        "tracked_object": stage.tracked_object,
        "visible_seconds": stage.visible_seconds,
        "status": stage.status,
    }


def _cycle_payload(cycle, include_stages=True):
    duration = _duration(cycle.started_at, cycle.ended_at)
    data = {
        "id": cycle.id,
        "cycle_id": cycle.cycle_id,
        "device_id": cycle.device_id,
        "front": cycle.front,
        "shift": cycle.shift,
        "started_at": _iso(cycle.started_at),
        "ended_at": _iso(cycle.ended_at),
        "duration_seconds": duration,
        "target_duration_seconds": cycle.target_duration_seconds,
        "deviation_seconds": duration - cycle.target_duration_seconds,
        "advance_meters": cycle.advance_meters,
        "status": cycle.status,
    }
    if include_stages:
        data["stages"] = [
            _stage_payload(stage)
            for stage in sorted(cycle.stages, key=lambda item: item.sequence)
        ]
    return data


@router.get("/summary")
def cycle_summary(db: Session = Depends(get_db)):
    cycles = db.query(ExcavationCycle).order_by(ExcavationCycle.started_at.desc()).all()
    active = next((cycle for cycle in cycles if cycle.status == "IN_PROGRESS"), None)
    finished = [cycle for cycle in cycles if cycle.status == "COMPLETED"]
    avg_duration = (
        round(sum(_duration(c.started_at, c.ended_at) for c in finished) / len(finished))
        if finished else 0
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycles_total": len(cycles),
        "cycles_completed": len(finished),
        "average_duration_seconds": avg_duration,
        "advance_meters": round(sum(c.advance_meters or 0 for c in cycles), 2),
        "active_cycle": _cycle_payload(active) if active else None,
        "recent_cycles": [_cycle_payload(cycle, False) for cycle in cycles[:10]],
    }


@router.get("")
def list_cycles(limit: int = 50, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 500))
    cycles = db.query(ExcavationCycle).order_by(ExcavationCycle.started_at.desc()).limit(limit).all()
    return [_cycle_payload(cycle) for cycle in cycles]


@router.post("", status_code=201)
def create_cycle(payload: CycleCreate, db: Session = Depends(get_db)):
    if db.query(ExcavationCycle).filter(ExcavationCycle.cycle_id == payload.cycle_id).first():
        raise HTTPException(status_code=409, detail="El ciclo ya existe")
    values = payload.model_dump(exclude={"stages"})
    cycle = ExcavationCycle(**values)
    db.add(cycle)
    db.flush()
    for stage in payload.stages:
        db.add(CycleStage(cycle_id=cycle.id, **stage.model_dump()))
    db.commit()
    db.refresh(cycle)
    return _cycle_payload(cycle)


@router.post("/{cycle_id}/stages", status_code=201)
def add_stage(cycle_id: str, payload: StageCreate, db: Session = Depends(get_db)):
    cycle = db.query(ExcavationCycle).filter(ExcavationCycle.cycle_id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Ciclo no encontrado")
    stage = CycleStage(cycle_id=cycle.id, **payload.model_dump())
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return _stage_payload(stage)
