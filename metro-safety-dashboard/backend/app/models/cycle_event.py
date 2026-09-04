from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
import datetime


class ExcavationCycle(Base):
    __tablename__ = "excavation_cycles"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(String, unique=True, index=True, nullable=False)
    device_id = Column(String, index=True, nullable=False)
    front = Column(String, index=True, default="Frente Norte")
    shift = Column(String, index=True, default="Día")
    started_at = Column(DateTime, index=True, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    target_duration_seconds = Column(Integer, default=17100)
    advance_meters = Column(Float, default=0.0)
    status = Column(String, default="IN_PROGRESS", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    stages = relationship(
        "CycleStage", back_populates="cycle", cascade="all, delete-orphan"
    )


class CycleStage(Base):
    __tablename__ = "cycle_stages"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("excavation_cycles.id"), index=True)
    stage_code = Column(String, index=True, nullable=False)
    stage_name = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    started_at = Column(DateTime, index=True, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    target_duration_seconds = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    evidence_url = Column(String, nullable=True)
    tracked_object = Column(String, nullable=True)
    visible_seconds = Column(Integer, default=0)
    status = Column(String, default="IN_PROGRESS")

    cycle = relationship("ExcavationCycle", back_populates="stages")
