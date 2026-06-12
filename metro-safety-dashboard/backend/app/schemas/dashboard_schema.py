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
    total_large_rocks_detections: int
    total_landslide_detections: int
    current_risk_level: str
    total_alarms_triggered: int
