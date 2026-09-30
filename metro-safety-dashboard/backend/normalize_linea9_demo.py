"""Corrige únicamente el ciclo sembrado L9-DEMO-001 en la base activa."""
from datetime import datetime, timedelta

from app.database.session import SessionLocal
from app.models.cycle_event import ExcavationCycle, CycleStage


DEMO_CYCLE_ID = "L9-DEMO-001"
STAGES = [
    ("excavation", 72, 80),
    ("topography", 16, 20),
    ("partial_seal", 36, 40),
    ("mesh_frames", 130, 130),
    ("hp1", 18, 15),
]

db = SessionLocal()
try:
    cycle = (
        db.query(ExcavationCycle)
        .filter(ExcavationCycle.cycle_id == DEMO_CYCLE_ID)
        .first()
    )
    if cycle is None:
        print(f"No se encontró {DEMO_CYCLE_ID}; no se modificó ningún dato.")
        raise SystemExit(0)

    # La muestra queda cerrada: su duración no seguirá creciendo con el tiempo.
    ended_at = datetime.utcnow()
    started_at = ended_at - timedelta(hours=4, minutes=32)
    cycle.started_at = started_at
    cycle.ended_at = ended_at
    cycle.target_duration_seconds = 4 * 60 * 60 + 45 * 60
    cycle.status = "COMPLETED"
    cycle.advance_meters = 0.9

    offset = 0
    for stage_code, duration_minutes, target_minutes in STAGES:
        stage_start = started_at + timedelta(minutes=offset)
        offset += duration_minutes
        stage = (
            db.query(CycleStage)
            .filter(
                CycleStage.cycle_id == cycle.id,
                CycleStage.stage_code == stage_code,
            )
            .first()
        )
        if stage is None:
            continue
        stage.started_at = stage_start
        stage.ended_at = stage.started_at + timedelta(minutes=duration_minutes)
        stage.target_duration_seconds = target_minutes * 60
        stage.status = "COMPLETED"

    db.commit()
    print(
        f"{DEMO_CYCLE_ID} actualizado: completado en 4 h 32 min; "
        "objetivo 4 h 45 min. Origen LoRaWAN sigue sin verificar."
    )
except Exception:
    db.rollback()
    raise
finally:
    db.close()
