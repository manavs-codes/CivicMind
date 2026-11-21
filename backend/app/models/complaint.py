
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, timezone


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

    location: str
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
    location: Optional[str] = None