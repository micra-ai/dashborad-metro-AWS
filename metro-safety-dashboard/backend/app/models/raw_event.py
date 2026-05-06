from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database.connection import Base
import datetime

class RawEvent(Base):
    __tablename__ = "raw_events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String, index=True)
    schema_version = Column(String)
    device_id = Column(String, index=True)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    raw_payload = Column(Text)
    validation_status = Column(String)
    validation_errors = Column(Text, nullable=True)
