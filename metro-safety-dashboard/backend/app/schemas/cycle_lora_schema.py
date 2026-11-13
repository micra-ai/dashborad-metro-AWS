from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CycleLoRaObject(BaseModel):
    event_type: Literal["CYCLE_START", "STAGE_START", "STAGE_END", "CYCLE_END", "HEARTBEAT_STATUS"]
    cycle_id: Optional[str] = Field(default=None, min_length=1, max_length=100)
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

    camera_online: Optional[bool] = None
    active_sequence: Optional[int] = Field(default=None, ge=1)
    active_stage_code: Optional[str] = None
    daily_completed_cycles: Optional[int] = Field(default=None, ge=0)
    pending_offline_queue: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def require_cycle_id(self):
        if self.event_type != "HEARTBEAT_STATUS" and not self.cycle_id:
            raise ValueError("cycle_id es obligatorio para eventos de ciclo")
        return self


class CycleLoRaUplinkPayload(BaseModel):


    @model_validator(mode="before")

    @classmethod

    def accept_flat_milesight_payload(cls, value):

        if not isinstance(value, dict):

            return value

        if "object" in value or "event_type" not in value:

            return value

        result = dict(value)

        result["object"] = {

            key: value[key]

            for key in CycleLoRaObject.model_fields

            if key in value

        }

        return result




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
