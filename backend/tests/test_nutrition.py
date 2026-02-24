from __future__ import annotations

from httpx import AsyncClient

from app.services.nutrition_service import calculate_bmr, calculate_calorie_target, calculate_tdee


async def _register_and_login(client: AsyncClient, email: str, username: str) -> str:
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "testpass123"},
    )
    assert reg.status_code == 201
    return reg.json()["access_token"]


async def test_calculate_bmr_male():
    # Male, 80kg, 180cm, 30 years old
    # Expected: 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    result = calculate_bmr(80.0, 180.0, 30.0, "male")
    assert abs(result - 1780.0) < 0.1


async def test_calculate_bmr_female():
    # Female, 60kg, 165cm, 25 years old
    # Expected: 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
    result = calculate_bmr(60.0, 165.0, 25.0, "female")
    assert abs(result - 1345.25) < 0.1


async def test_tdee_activity_multipliers():
    bmr = 1800.0
    assert abs(calculate_tdee(bmr, "sedentary") - 1800 * 1.2) < 0.1
    assert abs(calculate_tdee(bmr, "moderate") - 1800 * 1.55) < 0.1
    assert abs(calculate_tdee(bmr, "very_active") - 1800 * 1.9) < 0.1


async def test_calorie_target_goals():
    tdee = 2500.0
    assert calculate_calorie_target(tdee, "lose_weight") == 2000.0
    assert calculate_calorie_target(tdee, "maintain") == 2500.0
    assert calculate_calorie_target(tdee, "build_muscle") == 2800.0


async def test_log_meal_and_retrieve(client: AsyncClient):
    token = await _register_and_login(client, "meal@example.com", "mealuser")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a food item
    food_resp = await client.post(
        "/api/v1/nutrition/foods",
        headers=headers,
        json={
            "name": "Chicken Breast",
            "calories_per_100g": 165.0,
            "protein_per_100g": 31.0,
            "carbs_per_100g": 0.0,
            "fat_per_100g": 3.6,
        },
    )
    assert food_resp.status_code == 201
    food_id = food_resp.json()["id"]

    # Log a meal
    meal_resp = await client.post(
        "/api/v1/nutrition/meals",
        headers=headers,
        params={"log_date": "2024-06-01"},
        json={"food_item_id": food_id, "meal_type": "lunch", "amount_g": 200.0},
    )
    assert meal_resp.status_code == 200

    # Get the day's log
    log_resp = await client.get(
        "/api/v1/nutrition/log",
        headers=headers,
        params={"log_date": "2024-06-01"},
    )
    assert log_resp.status_code == 200
    data = log_resp.json()
    assert len(data["meals"]) == 1
    assert abs(data["meals"][0]["calories"] - 330.0) < 1.0  # 165 * 200/100


async def test_tdee_endpoint_requires_profile(client: AsyncClient):
    token = await _register_and_login(client, "notdee@example.com", "nodeeuser")
    headers = {"Authorization": f"Bearer {token}"}

    # User has no profile — should return 422
    resp = await client.get("/api/v1/nutrition/tdee", headers=headers)
    assert resp.status_code == 422


async def test_tdee_endpoint_with_profile(client: AsyncClient):
    token = await _register_and_login(client, "tdee@example.com", "tdeeuser")
    headers = {"Authorization": f"Bearer {token}"}

    # Update profile with required TDEE fields
    profile_resp = await client.put(
        "/api/v1/users/me/profile",
        headers=headers,
        json={
            "weight_kg": 80.0,
            "height_cm": 180.0,
            "date_of_birth": "1993-01-01T00:00:00Z",
            "gender": "male",
            "activity_level": "moderate",
            "fitness_goal": "maintain",
        },
    )
    assert profile_resp.status_code == 200

    tdee_resp = await client.get("/api/v1/nutrition/tdee", headers=headers)
    assert tdee_resp.status_code == 200
    data = tdee_resp.json()
    assert "bmr" in data
    assert "tdee" in data
    assert "calorie_target" in data
    assert data["tdee"] > data["bmr"]  # TDEE should be higher than BMR
