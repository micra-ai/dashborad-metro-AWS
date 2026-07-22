from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database.connection import Base
import datetime

class ExcavationEvent(Base):
    __tablename__ = "excavation_events"
    id = Column(Integer, primary_key=True, index=True)
    raw_event_id = Column(Integer, index=True)
    event_id = Column(String, unique=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime)
    site = Column(String)
    area = Column(String)
    zone = Column(String)
    large_rocks_detected = Column(Boolean, default=False)
    large_rocks_count = Column(Integer, default=0)
    landslide_detected = Column(Boolean, default=False)
    landslide_count = Column(Integer, default=0)
    movement_detected = Column(Boolean, default=False)
    avance_metros = Column(Float, default=0.0)
    risk_level = Column(String)
    confidence = Column(Float, default=0.0)
    alarm_triggered = Column(Boolean, default=False)
    alarm_type = Column(String, nullable=True)
    alarm_level = Column(String, nullable=True)
    trigger_reason = Column(String, nullable=True)
    activation_duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
