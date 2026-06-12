from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class Location(BaseModel):
    site: str
    area: str
    zone: str
    camera_position: Optional[str] = None

class DetectionWindow(BaseModel):
    start_time: str
    end_time: str
    duration_seconds: int

class PpeItem(BaseModel):
    detected: bool
    confidence: float

class PpeDict(BaseModel):
    helmet: Optional[PpeItem] = None
    gloves: Optional[PpeItem] = None
    goggles: Optional[PpeItem] = None
    reflective_vest: Optional[PpeItem] = None
    mask: Optional[PpeItem] = None

class Worker(BaseModel):
    temporary_tracking_id: str
    confidence: float
    ppe: PpeDict
    compliance_status: str
    missing_ppe: List[str]

class Alerts(BaseModel):
    non_compliance_detected: bool
    critical_missing_ppe: bool
    alert_level: str

class Summary(BaseModel):
    workers_detected: int
    workers_full_compliance: int
    workers_partial_compliance: int
    workers_without_required_ppe: int
    overall_compliance_percentage: float

class EppEventPayload(BaseModel):
    event_type: str
    schema_version: str
    event_id: str
    device_id: str
    device_type: str
    client: str
    location: Location
    timestamp: str
    detection_window: DetectionWindow
    summary: Summary
    workers: List[Worker]
    alerts: Alerts
    image_base64: Optional[str] = None
    raw_metadata: Dict[str, Any]
