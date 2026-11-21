
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class Complaint(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    category: str
    location: str
    status: str = "Pending"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ComplaintUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    location: Optional[str] = None