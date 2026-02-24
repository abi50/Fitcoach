from __future__ import annotations

from app.services.recovery_service import calculate_recovery_score


async def _register_and_login(client, email: str, username: str) -> str:
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "testpass123"},
    )
    assert reg.status_code == 201
    return reg.json()["access_token"]


async def test_recovery_score_full_sleep():
    # 8h sleep (ideal), quality=5, fatigue=1 (lowest fatigue)
    score = calculate_recovery_score(sleep_hours=8.0, sleep_quality=5, fatigue_level=1)
    # sleep: 40pts, quality: 20pts, fatigue: (10-1)/9*25=25pts, training: 15pts = 100pts
    assert score > 90.0


async def test_recovery_score_poor_sleep():
    # 4h sleep (minimum for any points), quality=1, fatigue=9 (very fatigued)
    score = calculate_recovery_score(sleep_hours=4.0, sleep_quality=1, fatigue_level=9)
    # sleep: 0pts (4h = 0), quality: 4pts (1/5*20), fatigue: ~2.78pts ((10-9)/9*25)
    assert score < 25.0


async def test_recovery_score_missing_data():
    # All None inputs — should return a reasonable default, not crash
    score = calculate_recovery_score(sleep_hours=None, sleep_quality=None, fatigue_level=None)
    # default: sleep=20, quality=10, fatigue=12.5, training=15 = 57.5
    assert 40.0 < score < 70.0


async def test_log_recovery_computes_score(client):
    token = await _register_and_login(client, "rec@example.com", "recuser")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/recovery/checkin",
        headers=headers,
        json={
            "log_date": "2024-06-01",
            "sleep_hours": 8.0,
            "sleep_quality": 4,
            "fatigue_level": 3,
            "soreness": [],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "recovery_score" in data
    assert data["recovery_score"] is not None
    assert 0.0 <= data["recovery_score"] <= 100.0
    # With 8h sleep, quality=4, fatigue=3, score should be decent
    assert data["recovery_score"] > 50.0
