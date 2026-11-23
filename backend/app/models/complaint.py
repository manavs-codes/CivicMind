
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Literal
from datetime import datetime, timezone

class ComplaintLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str = Field(..., min_length=3)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_coordinates(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError(
                "Latitude and longitude must both be provided or both be null"
            )
        return self
    
class Complaint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    category: Literal[
        "Pothole / Road Damage",
        "Garbage / Waste Management",
        "Streetlight",
        "Water Leakage",
        "Drainage / Sewage",
        "Other"
    ]

    location: ComplaintLocation
    status: Literal["Pending"] = "Pending"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class ComplaintUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[Literal[
        "Pothole / Road Damage",
        "Garbage / Waste Management",
        "Streetlight",
        "Water Leakage",
        "Drainage / Sewage",
        "Other"
    ]] = None
    location: Optional[ComplaintLocation] = None

    @model_validator(mode="after")
    def reject_explicit_nulls(self):
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self