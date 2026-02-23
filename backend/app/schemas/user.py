from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, EmailStr


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: datetime | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    fitness_goal: str | None = None
    activity_level: str | None = None
    experience_level: str | None = None
    available_equipment: list[str] | None = None
    dietary_restrictions: list[str] | None = None
    units: str | None = None


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    first_name: str | None
    last_name: str | None
    gender: str | None
    height_cm: float | None
    weight_kg: float | None
    fitness_goal: str | None
    activity_level: str | None
    experience_level: str | None
    available_equipment: list[str] | None
    dietary_restrictions: list[str] | None
    units: str
    avatar_url: str | None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    profile: UserProfileResponse | None

    class Config:
        from_attributes = True
