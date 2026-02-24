from __future__ import annotations


def calculate_recovery_score(
    sleep_hours: float | None,
    sleep_quality: int | None,         # 1-5
    fatigue_level: int | None,          # 1-10 (higher = more fatigued)
    training_load_score: float | None = None,  # 0-1 pre-computed
) -> float:
    """Return a 0–100 composite recovery score.

    Components:
    - Sleep hours vs 7-9h target: 40 pts
      - <4h or >12h: 0 pts
      - 4-7h: scale linearly from 0 to 40
      - 7-9h: 40 pts (peak)
      - 9-12h: scale linearly from 40 down to 20 (over-sleep penalty)
    - Sleep quality 1-5: 20 pts (quality/5 * 20)
    - Inverse fatigue 1-10: 25 pts ((10-fatigue)/9 * 25)
    - Training load past 3 days: 15 pts
      - None/no load: 15 pts
      - Scales based on training_load_score (0=15pts, 1=0pts)

    Returns clamped 0-100 float.
    """
    score = 0.0

    # Sleep hours component (40 pts)
    if sleep_hours is not None:
        h = sleep_hours
        if 7.0 <= h <= 9.0:
            sleep_score = 40.0
        elif h < 4.0 or h > 12.0:
            sleep_score = 0.0
        elif h < 7.0:
            # Linear scale from 4h (0 pts) to 7h (40 pts)
            sleep_score = (h - 4.0) / 3.0 * 40.0
        else:  # 9 < h <= 12
            # Slight penalty for oversleeping: 40 at 9h, 20 at 12h
            sleep_score = 40.0 - (h - 9.0) / 3.0 * 20.0
        score += sleep_score
    else:
        # Default to middle value
        score += 20.0

    # Sleep quality component (20 pts)
    if sleep_quality is not None:
        q = max(1, min(5, sleep_quality))
        score += (q / 5.0) * 20.0
    else:
        score += 10.0  # default middle

    # Inverse fatigue component (25 pts)
    if fatigue_level is not None:
        f = max(1, min(10, fatigue_level))
        score += ((10 - f) / 9.0) * 25.0
    else:
        score += 12.5  # default middle

    # Training load component (15 pts)
    if training_load_score is not None:
        load = max(0.0, min(1.0, training_load_score))
        score += (1.0 - load) * 15.0
    else:
        score += 15.0  # no training load = full 15 pts

    return max(0.0, min(100.0, score))
