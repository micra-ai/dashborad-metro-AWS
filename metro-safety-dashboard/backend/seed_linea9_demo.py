"""Carga una muestra del ciclo L9. Ejecutar una sola vez desde backend/."""
from datetime import datetime, timedelta
from app.database.connection import Base, engine
from app.database.session import SessionLocal
from app.models.cycle_event import ExcavationCycle, CycleStage

Base.metadata.create_all(bind=engine)
db = SessionLocal()
if db.query(ExcavationCycle).filter_by(cycle_id="L9-DEMO-001").first():
    print("Los datos demo ya existen")
    raise SystemExit(0)

start = datetime.utcnow() - timedelta(hours=4, minutes=32)
cycle = ExcavationCycle(cycle_id="L9-DEMO-001", device_id="camera-01", front="Frente Norte", shift="Día", started_at=start, target_duration_seconds=17100, advance_meters=0.9, status="IN_PROGRESS")
db.add(cycle); db.flush()
definitions = [
    ("excavation", "Excavación y perfilado", 0, 72, 80, "excavadora", "COMPLETED"),
    ("topography", "Chequeo topográfico", 72, 16, 20, "topografo", "COMPLETED"),
    ("partial_seal", "Sellado parcial", 88, 36, 40, "equipo_hormigon", "COMPLETED"),
    ("mesh_frames", "Malla 1 y marcos", 124, 130, 120, "malla_marco", "COMPLETED"),
    ("hp1", "Proyección HP1", 254, None, 35, "brazo_hp1", "IN_PROGRESS"),
]
for sequence, (code, name, offset, length, target, tracked, status) in enumerate(definitions, 1):
    stage_start = start + timedelta(minutes=offset)
    db.add(CycleStage(cycle_id=cycle.id, stage_code=code, stage_name=name, sequence=sequence, started_at=stage_start, ended_at=stage_start + timedelta(minutes=length) if length else None, target_duration_seconds=target * 60, confidence=0.91, tracked_object=tracked, visible_seconds=768 if code == "hp1" else 0, status=status))
db.commit(); db.close()
print("Datos demo de Línea 9 creados")
