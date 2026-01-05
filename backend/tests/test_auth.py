"""
Unit tests for authentication endpoints
Uses the actual test database (test_betsan.db)
"""
import pytest
import os

os.environ["ENVIRONMENT"] = "testing"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestLogin:
    def test_login_success(self):
        """Test login with admin user from init_db.py"""
        response = client.post(
            "/api/auth/login",
            data={"username": "admin@betsan.com", "password": "admin123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_wrong_password(self):
        response = client.post(
            "/api/auth/login",
            data={"username": "admin@betsan.com", "password": "wrong"}
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        response = client.post(
            "/api/auth/login",
            data={"username": "nobody@test.com", "password": "pass"}
        )
        assert response.status_code == 401


class TestMe:
    def test_get_current_user(self):
        """Login and get user info"""
        # Login
        login = client.post(
            "/api/auth/login",
            data={"username": "admin@betsan.com", "password": "admin123"}
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        
        # Get me
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@betsan.com"
        assert data["role"] == "admin"
    
    def test_get_current_user_unauthorized(self):
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert response.status_code == 401


class TestLogout:
    def test_logout(self):
        login = client.post(
            "/api/auth/login",
            data={"username": "admin@betsan.com", "password": "admin123"}
        )
        token = login.json()["access_token"]
        
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
