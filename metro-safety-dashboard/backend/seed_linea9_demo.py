"""Carga un ciclo de demostración completado y de duración plausible."""
from datetime import datetime, timedelta

from app.database.connection import Base, engine
from app.database.session import SessionLocal
from app.models.cycle_event import ExcavationCycle, CycleStage


Base.metadata.create_all(bind=engine)
db = SessionLocal()
if db.query(ExcavationCycle).filter_by(cycle_id="L9-DEMO-001").first():
    print("Los datos demo ya existen; use normalize_linea9_demo.py para corregirlos.")
    raise SystemExit(0)

end = datetime.utcnow()
start = end - timedelta(hours=4, minutes=32)
cycle = ExcavationCycle(
    cycle_id="L9-DEMO-001",
    device_id="camera-01",
    front="Frente Norte",
    shift="Día",
    started_at=start,
    ended_at=end,
    target_duration_seconds=4 * 60 * 60 + 45 * 60,
    advance_meters=0.9,
    status="COMPLETED",
)
db.add(cycle)
db.flush()

# Duraciones reales de muestra: suman 4 h 32 min; objetivos, 4 h 45 min.
definitions = [
    ("excavation", "Excavación y perfilado", 72, 80, "excavadora"),
    ("topography", "Chequeo topográfico", 16, 20, "topografo"),
    ("partial_seal", "Sellado parcial", 36, 40, "equipo_hormigon"),
    ("mesh_frames", "Malla 1 y marcos", 130, 130, "malla_marco"),
    ("hp1", "Proyección HP1", 18, 15, "brazo_hp1"),
]
offset = 0
for sequence, (code, name, duration_minutes, target_minutes, tracked) in enumerate(definitions, 1):
    stage_start = start + timedelta(minutes=offset)
    stage_end = stage_start + timedelta(minutes=duration_minutes)
    db.add(
        CycleStage(
            cycle_id=cycle.id,
            stage_code=code,
            stage_name=name,
            sequence=sequence,
            started_at=stage_start,
            ended_at=stage_end,
            target_duration_seconds=target_minutes * 60,
            confidence=0.91,
            tracked_object=tracked,
            visible_seconds=768 if code == "hp1" else 0,
            status="COMPLETED",
        )
    )
    offset += duration_minutes

db.commit()
db.close()
print("Ciclo demo L9-DEMO-001 creado como completado (4 h 32 min; origen LoRaWAN no verificado).")
