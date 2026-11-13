from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database.connection import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    raw_event_id = Column(Integer, ForeignKey("raw_events.id"), nullable=False, unique=True)
    device_id = Column(String(100), nullable=False, index=True)
    location = Column(String(20), nullable=False, index=True)
    measured_at = Column(DateTime, nullable=False, index=True)
    temperature_c = Column(Float, nullable=False)
    co2_ppm = Column(Float, nullable=True)


class ConstructionActivity(Base):
    __tablename__ = "construction_activities"
    id = Column(Integer, primary_key=True)
    raw_event_id = Column(Integer, ForeignKey("raw_events.id"), nullable=False, unique=True)
    device_id = Column(String(100), nullable=False, index=True)
    cycle_id = Column(String(100), nullable=False, index=True)
    detected_stage_code = Column(String(100), nullable=False)
    classified_stage_code = Column(String(100), nullable=False, index=True)
    classification_status = Column(String(30), nullable=False)
    estado_sello = Column(String(20), nullable=False)
    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
