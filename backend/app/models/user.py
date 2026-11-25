
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")


class UserPublic(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: Literal["citizen", "admin"]
    created_at: datetime
    is_active: bool


class UserInDB(BaseModel):
    full_name: str
    email: EmailStr
    password_hash: str
    role: Literal["citizen", "admin"] = "citizen"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")
