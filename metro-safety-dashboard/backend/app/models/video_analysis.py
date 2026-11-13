from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.database.connection import Base


class VideoAnalysis(Base):
    __tablename__ = 'video_analyses'
    analysis_id = Column(String(64), primary_key=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    payload = Column(JSON, nullable=False)
