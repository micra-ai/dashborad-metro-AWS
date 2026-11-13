from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator


class VideoSegment(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    stage_code: str = Field(min_length=1, max_length=80)
    stage_name: str = Field(min_length=1, max_length=120)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    visible_seconds: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    observation: Literal['STAGE_CANDIDATE', 'OBJECT_PRESENT', 'UNOBSERVED']
    tracked_object: str = Field(default='', max_length=120)

    @model_validator(mode='after')
    def interval(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError('El término debe ser posterior al inicio')
        if self.visible_seconds > self.end_seconds - self.start_seconds + 0.01:
            raise ValueError('Tiempo visible mayor que el intervalo')
        return self


class VideoResult(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    schema_version: Literal[1] = 1
    analysis_id: str = Field(pattern=r'^[a-f0-9]{64}$')
    video_original: str = Field(min_length=1, max_length=255)
    device_id: str = Field(min_length=1, max_length=100)
    front: str = Field(default='Frente Norte', max_length=100)
    shift: str = Field(default='Sin informar', max_length=60)
    recorded_at: datetime | None = None
    cycle_reference: str | None = Field(default=None, max_length=100)
    duration_seconds: float = Field(gt=0, le=86400 * 7)
    sample_seconds: float | None = Field(default=None, gt=0, le=60)
    model_classes: list[str] = Field(default_factory=list, max_length=200)
    mapped_classes: list[str] = Field(default_factory=list, max_length=200)
    segments: list[VideoSegment] = Field(max_length=20000)
    warnings: list[str] = Field(default_factory=list, max_length=50)

    @model_validator(mode='after')
    def bounds(self):
        if self.recorded_at is not None and self.recorded_at.utcoffset() is None:
            raise ValueError('recorded_at requiere zona horaria, por ejemplo -03:00')
        if any(s.end_seconds > self.duration_seconds + 0.01 for s in self.segments):
            raise ValueError('Intervalo fuera de la duración del video')
        return self
