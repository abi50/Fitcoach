from __future__ import annotations

from httpx import AsyncClient


async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_register_happy_path(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "username": "alice",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = {
        "email": "bob@example.com",
        "username": "bob",
        "password": "securepassword123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    duplicate = await client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "username": "bob2", "password": "otherpass123"},
    )
    assert duplicate.status_code == 409


async def test_login_happy_path(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "carol@example.com",
            "username": "carol",
            "password": "mypassword123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "mypassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dave@example.com",
            "username": "dave",
            "password": "correctpassword",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
