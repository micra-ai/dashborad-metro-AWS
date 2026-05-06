from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database.connection import Base
import datetime

class EppEvent(Base):
    __tablename__ = "epp_events"
    id = Column(Integer, primary_key=True, index=True)
    raw_event_id = Column(Integer, index=True)
    event_id = Column(String, unique=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime)
    site = Column(String)
    area = Column(String)
    zone = Column(String)
    workers_detected = Column(Integer, default=0)
    workers_full_compliance = Column(Integer, default=0)
    workers_partial_compliance = Column(Integer, default=0)
    workers_without_required_ppe = Column(Integer, default=0)
    overall_compliance_percentage = Column(Float, default=0.0)
    missing_helmet_count = Column(Integer, default=0)
    missing_gloves_count = Column(Integer, default=0)
    missing_goggles_count = Column(Integer, default=0)
    missing_reflective_vest_count = Column(Integer, default=0)
    missing_mask_count = Column(Integer, default=0)
    alert_level = Column(String)
    non_compliance_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
