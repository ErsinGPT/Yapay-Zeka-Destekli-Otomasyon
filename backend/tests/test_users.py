"""
Unit tests for users endpoints
Uses the actual test database (test_otomasyon.db)
"""
import pytest
import os

os.environ["ENVIRONMENT"] = "testing"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_admin_token():
    """Helper to get admin token"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@otomasyon.com", "password": "admin123"}
    )
    return response.json()["access_token"]


class TestGetUsers:
    def test_get_users_as_admin(self):
        token = get_admin_token()
        response = client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 1
        assert any(u["email"] == "admin@otomasyon.com" for u in users)
    
    def test_get_users_unauthorized(self):
        response = client.get("/api/users/")
        assert response.status_code == 401


class TestGetMe:
    def test_get_my_profile(self):
        token = get_admin_token()
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "admin@otomasyon.com"


class TestGetRoles:
    def test_get_roles(self):
        token = get_admin_token()
        response = client.get(
            "/api/users/roles",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) >= 1
        assert any(r["name"] == "admin" for r in roles)
