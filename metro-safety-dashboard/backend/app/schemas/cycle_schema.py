from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class StageCreate(BaseModel):
    stage_code: str
    stage_name: str
    sequence: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    target_duration_seconds: int = 0
    confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_url: Optional[str] = None
    tracked_object: Optional[str] = None
    visible_seconds: int = 0
    status: str = "IN_PROGRESS"


class CycleCreate(BaseModel):
    cycle_id: str
    device_id: str
    front: str = "Frente Norte"
    shift: str = "Día"
    started_at: datetime
    ended_at: Optional[datetime] = None
    target_duration_seconds: int = 17100
    advance_meters: float = 0.0
    status: str = "IN_PROGRESS"
    stages: List[StageCreate] = Field(default_factory=list)
