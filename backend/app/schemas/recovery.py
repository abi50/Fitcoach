from __future__ import annotations
from datetime import date
from pydantic import BaseModel


class MuscleSorenessCreate(BaseModel):
    muscle_group: str
    soreness_level: int  # 1-5


class RecoveryCheckinCreate(BaseModel):
    log_date: date | None = None
    sleep_hours: float | None = None
    sleep_quality: int | None = None  # 1-5
    fatigue_level: int | None = None  # 1-10
    stress_level: int | None = None  # 1-10
    mood: int | None = None  # 1-5
    notes: str | None = None
    soreness: list[MuscleSorenessCreate] = []


class RecoveryLogResponse(BaseModel):
    id: str
    log_date: date
    sleep_hours: float | None
    sleep_quality: int | None
    fatigue_level: int | None
    stress_level: int | None
    mood: int | None
    recovery_score: float | None
    notes: str | None
    soreness_entries: list[dict]

    class Config:
        from_attributes = True
