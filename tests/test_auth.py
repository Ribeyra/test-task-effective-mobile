import pytest
from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        payload = {
            "email": "newuser@test.com",
            "password": "secret123",
            "password_confirm": "secret123",
            "first_name": "New",
            "last_name": "User",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newuser@test.com"
        assert data["first_name"] == "New"
        assert data["is_active"] is True
        assert "password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, seed_data: dict):
        payload = {
            "email": "admin@test.com",
            "password": "secret123",
            "password_confirm": "secret123",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    async def test_register_password_mismatch(self, client: AsyncClient):
        payload = {
            "email": "mismatch@test.com",
            "password": "secret123",
            "password_confirm": "different",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "do not match" in resp.json()["detail"]

    async def test_register_short_password(self, client: AsyncClient):
        payload = {
            "email": "short@test.com",
            "password": "ab",
            "password_confirm": "ab",
        }
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, seed_data: dict):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, seed_data: dict):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "wrong",
        })
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    async def test_login_nonexistent_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "secret123",
        })
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["detail"] == "Logged out successfully"

    async def test_logout_no_token(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 401


class TestGetMe:
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@test.com"
        assert data["is_superuser"] is True

    async def test_get_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401
