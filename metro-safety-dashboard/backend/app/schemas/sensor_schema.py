from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, field_validator


class ExteriorReading(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    event_id: str = Field(min_length=1, max_length=100)
    device_id: str = Field(min_length=1, max_length=100)
    measured_at: AwareDatetime
    temperature_c: float = Field(ge=-80, le=100)

    @field_validator("device_id")
    @classmethod
    def uppercase_device(cls, value):
        return value.upper()


class InteriorReading(ExteriorReading):
    co2_ppm: float = Field(ge=0, le=1000000)
