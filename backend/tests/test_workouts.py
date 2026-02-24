from __future__ import annotations

from httpx import AsyncClient

from app.services.workout_service import calculate_session_volume


async def register_and_login(
    client: AsyncClient,
    email: str = "w@example.com",
    username: str = "wuser",
    password: str = "pass123456",
) -> str:
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    return reg.json()["access_token"]


async def test_start_session(client: AsyncClient):
    token = await register_and_login(client)
    response = await client.post(
        "/api/v1/workouts/sessions",
        json={"started_at": "2024-01-01T10:00:00Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "id" in response.json()


async def test_calculate_session_volume_unit():
    class MockSet:
        def __init__(self, weight_kg: float, reps: int) -> None:
            self.weight_kg = weight_kg
            self.reps = reps

    sets = [MockSet(100, 5), MockSet(80, 8), MockSet(0, 10)]
    result = calculate_session_volume(sets)
    assert result == 100 * 5 + 80 * 8 + 0 * 10  # 500 + 640 + 0 = 1140


async def test_log_set_updates_session(client: AsyncClient):
    token = await register_and_login(client, email="log@example.com", username="loguser")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a custom exercise
    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        json={"name": "Bench Press", "category": "strength"},
        headers=headers,
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    # Start a session
    sess_resp = await client.post(
        "/api/v1/workouts/sessions",
        json={"started_at": "2024-01-01T10:00:00Z"},
        headers=headers,
    )
    assert sess_resp.status_code == 201
    session_id = sess_resp.json()["id"]

    # Log a set
    set_resp = await client.post(
        f"/api/v1/workouts/sessions/{session_id}/sets",
        json={
            "exercise_id": exercise_id,
            "set_number": 1,
            "weight_kg": 100.0,
            "reps": 5,
        },
        headers=headers,
    )
    assert set_resp.status_code == 201

    # Complete the session
    complete_resp = await client.post(
        f"/api/v1/workouts/sessions/{session_id}/complete",
        headers=headers,
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["total_volume_kg"] == 500.0


async def test_session_history_pagination(client: AsyncClient):
    token = await register_and_login(client, email="page@example.com", username="pageuser")
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 sessions with different started_at values
    for i in range(3):
        resp = await client.post(
            "/api/v1/workouts/sessions",
            json={"started_at": f"2024-01-0{i + 1}T10:00:00Z"},
            headers=headers,
        )
        assert resp.status_code == 201

    # Fetch page 1 with page_size=2 — should return exactly 2
    resp = await client.get(
        "/api/v1/workouts/sessions?page=1&page_size=2",
        headers=headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 2
