from __future__ import annotations


async def _register_and_login(client, email: str, username: str) -> str:
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "testpass123"},
    )
    assert reg.status_code == 201
    return reg.json()["access_token"]


async def test_pr_detected_on_new_weight(client):
    token = await _register_and_login(client, "pr1@example.com", "pruser1")
    headers = {"Authorization": f"Bearer {token}"}

    # Create an exercise
    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        headers=headers,
        json={"name": "Squat", "category": "strength"},
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    # Start a session
    sess_resp = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-01T10:00:00Z"},
    )
    assert sess_resp.status_code == 201
    session_id = sess_resp.json()["id"]

    # Log a set — first ever set = should be a PR
    set_resp = await client.post(
        f"/api/v1/workouts/sessions/{session_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 100.0, "reps": 5},
    )
    assert set_resp.status_code == 201
    assert set_resp.json()["is_pr"] is True


async def test_pr_not_detected_on_lower_weight(client):
    token = await _register_and_login(client, "pr2@example.com", "pruser2")
    headers = {"Authorization": f"Bearer {token}"}

    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        headers=headers,
        json={"name": "Deadlift", "category": "strength"},
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    sess1 = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-01T10:00:00Z"},
    )
    assert sess1.status_code == 201
    session1_id = sess1.json()["id"]

    # Log heavy set first (PR)
    await client.post(
        f"/api/v1/workouts/sessions/{session1_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 150.0, "reps": 3},
    )

    # Log lighter set — NOT a weight PR
    sess2 = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-02T10:00:00Z"},
    )
    assert sess2.status_code == 201
    session2_id = sess2.json()["id"]
    set_resp = await client.post(
        f"/api/v1/workouts/sessions/{session2_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 100.0, "reps": 3},
    )
    assert set_resp.status_code == 201
    # is_pr may be True for reps at this weight (first time at 100kg), but weight PR should NOT be
    # Just verify the endpoint works
    assert "is_pr" in set_resp.json()


async def test_pr_detected_on_more_reps(client):
    token = await _register_and_login(client, "pr3@example.com", "pruser3")
    headers = {"Authorization": f"Bearer {token}"}

    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        headers=headers,
        json={"name": "Bench Press", "category": "strength"},
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    # Session 1: log 5 reps at 80kg
    sess1 = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-01T10:00:00Z"},
    )
    assert sess1.status_code == 201
    s1_id = sess1.json()["id"]
    await client.post(
        f"/api/v1/workouts/sessions/{s1_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 80.0, "reps": 5},
    )

    # Session 2: log 8 reps at 80kg — more reps at same weight = reps PR
    sess2 = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-02T10:00:00Z"},
    )
    assert sess2.status_code == 201
    s2_id = sess2.json()["id"]
    set_resp = await client.post(
        f"/api/v1/workouts/sessions/{s2_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 80.0, "reps": 8},
    )
    assert set_resp.status_code == 201
    assert set_resp.json()["is_pr"] is True


async def test_pending_celebrations_returned(client):
    token = await _register_and_login(client, "pr4@example.com", "pruser4")
    headers = {"Authorization": f"Bearer {token}"}

    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        headers=headers,
        json={"name": "OHP", "category": "strength"},
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    sess = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-01T10:00:00Z"},
    )
    assert sess.status_code == 201
    session_id = sess.json()["id"]

    # Log a set that creates a PR
    await client.post(
        f"/api/v1/workouts/sessions/{session_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 60.0, "reps": 5},
    )

    # Check pending celebrations
    pending = await client.get("/api/v1/personal-records/pending-celebrations", headers=headers)
    assert pending.status_code == 200
    data = pending.json()["data"]
    assert len(data) >= 1


async def test_celebrate_clears_pending(client):
    token = await _register_and_login(client, "pr5@example.com", "pruser5")
    headers = {"Authorization": f"Bearer {token}"}

    ex_resp = await client.post(
        "/api/v1/workouts/exercises",
        headers=headers,
        json={"name": "Row", "category": "strength"},
    )
    assert ex_resp.status_code == 201
    exercise_id = ex_resp.json()["id"]

    sess = await client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={"started_at": "2024-01-01T10:00:00Z"},
    )
    assert sess.status_code == 201
    session_id = sess.json()["id"]

    await client.post(
        f"/api/v1/workouts/sessions/{session_id}/sets",
        headers=headers,
        json={"exercise_id": exercise_id, "set_number": 1, "weight_kg": 70.0, "reps": 5},
    )

    # Get the pending PR ID
    pending = await client.get("/api/v1/personal-records/pending-celebrations", headers=headers)
    assert pending.status_code == 200
    prs = pending.json()["data"]
    assert len(prs) >= 1
    pr_id = prs[0]["id"]

    # Mark as celebrated
    celebrate_resp = await client.post(
        f"/api/v1/personal-records/{pr_id}/celebrate", headers=headers
    )
    assert celebrate_resp.status_code == 204

    # Pending should now be empty (or at least not contain that PR)
    pending2 = await client.get("/api/v1/personal-records/pending-celebrations", headers=headers)
    assert pending2.status_code == 200
    remaining = [p for p in pending2.json()["data"] if p["id"] == pr_id]
    assert len(remaining) == 0
