from __future__ import annotations


def calculate_session_volume(sets: list) -> float:
    """Sum weight_kg * reps for all sets that have both values."""
    return sum((s.weight_kg or 0) * (s.reps or 0) for s in sets)
