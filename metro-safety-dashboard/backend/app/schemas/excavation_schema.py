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

class RiskDetection(BaseModel):
    large_rocks_detected: bool
    large_rocks_count: int
    landslide_detected: bool
    landslide_count: int
    movement_detected: bool
    risk_level: str
    confidence: float

class PositionReference(BaseModel):
    x_center: float
    y_center: float
    width: float
    height: float

class DetectedObject(BaseModel):
    object_type: str
    object_id: str
    confidence: float
    estimated_size_category: str
    position_reference: PositionReference

class Alarm(BaseModel):
    alarm_triggered: bool
    alarm_type: Optional[str] = None
    alarm_level: Optional[str] = None
    trigger_reason: Optional[str] = None
    triggered_at: Optional[str] = None
    activation_duration_seconds: Optional[int] = None

class ExcavationEventPayload(BaseModel):
    event_type: str
    schema_version: str
    event_id: str
    device_id: str
    device_type: str
    client: str
    location: Location
    timestamp: str
    detection_window: DetectionWindow
    risk_detection: RiskDetection
    detected_objects: List[DetectedObject]
    alarm: Alarm
    raw_metadata: Dict[str, Any]
