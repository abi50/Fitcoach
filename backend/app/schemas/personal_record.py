from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class PersonalRecordResponse(BaseModel):
    id: str
    exercise_id: str
    exercise_name: str
    weight_kg: float | None
    reps: int | None
    achieved_at: datetime
    pr_type: str
    previous_best: float | None
    celebrated: bool

    class Config:
        from_attributes = True
