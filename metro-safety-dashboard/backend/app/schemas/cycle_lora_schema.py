from typing import Literal, Optional

from pydantic import BaseModel, Field


class CycleLoRaObject(BaseModel):
    event_type: Literal["CYCLE_START", "STAGE_START", "STAGE_END", "CYCLE_END"]
    cycle_id: str = Field(min_length=1, max_length=100)
    stage_code: Optional[str] = None
    stage_name: Optional[str] = None
    sequence: Optional[int] = Field(default=None, ge=1)
    front: str = "Frente Norte"
    shift: str = "Día"
    target_duration_seconds: int = Field(default=0, ge=0)
    cycle_target_duration_seconds: int = Field(default=17100, ge=0)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    visible_seconds: int = Field(default=0, ge=0)
    confidence: float = Field(default=0.0, ge=0, le=1)
    evidence_url: Optional[str] = None
    tracked_object: Optional[str] = None
    advance_meters: float = Field(default=0.0, ge=0)


class CycleLoRaUplinkPayload(BaseModel):
    event: Optional[str] = "uplink"
    devEUI: str
    deviceName: Optional[str] = None
    applicationId: Optional[str] = None
    applicationName: Optional[str] = None
    fPort: Optional[int] = 3
    fCnt: Optional[int] = 0
    rssi: Optional[int] = 0
    snr: Optional[float] = 0.0
    timestamp: Optional[int] = None
    object: CycleLoRaObject
