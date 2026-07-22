from pydantic import BaseModel
from typing import Optional, Dict, Any

class DecodedObject(BaseModel):
    rocas_detectadas: int = 0
    deslizamientos: int = 0
    avance_metros: float = 0.0

class MilesightUplinkPayload(BaseModel):
    event: Optional[str] = "uplink"
    devEUI: str
    deviceName: Optional[str] = None
    applicationId: Optional[str] = None
    applicationName: Optional[str] = None
    fPort: Optional[int] = 2
    fCnt: Optional[int] = 0
    rssi: Optional[int] = 0
    snr: Optional[float] = 0.0
    data: Optional[str] = None
    object: Optional[DecodedObject] = None
    timestamp: Optional[int] = None
