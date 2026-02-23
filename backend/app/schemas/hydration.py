from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel


class HydrationEntryCreate(BaseModel):
    amount_ml: int
    beverage_type: str | None = None


class HydrationEntryResponse(BaseModel):
    id: str
    amount_ml: int
    beverage_type: str | None
    logged_at: datetime

    class Config:
        from_attributes = True


class HydrationLogResponse(BaseModel):
    id: str
    log_date: date
    target_ml: int
    total_ml: int
    entries: list[HydrationEntryResponse]
    percentage: float

    class Config:
        from_attributes = True


class HydrationTargetUpdate(BaseModel):
    target_ml: int
