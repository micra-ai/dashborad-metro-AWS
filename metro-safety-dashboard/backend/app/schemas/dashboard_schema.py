from pydantic import BaseModel
from typing import List, Optional

class DashboardSummary(BaseModel):
    total_events: int
    last_update: str
    active_devices_count: int

class EppSummary(BaseModel):
    total_workers_detected: int
    overall_compliance_percentage: float
    workers_full_compliance: int
    workers_partial_compliance: int
    positive_compliance_count: int
    negative_compliance_count: int
    most_frequent_missing_ppe: Optional[str]

class ExcavationSummary(BaseModel):
    rocas_detectadas: int = 0
    deslizamientos: int = 0
    avance_metros: float = 0.0
    device_status: str = "Offline"
    last_seen: Optional[str] = None
    total_large_rocks_detections: int = 0
    total_landslide_detections: int = 0
    current_risk_level: str = "LOW"
    total_alarms_triggered: int = 0
