from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.connection import Base
import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    device_type = Column(String, nullable=False)
    client = Column(String)
    site = Column(String)
    area = Column(String)
    zone = Column(String)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
