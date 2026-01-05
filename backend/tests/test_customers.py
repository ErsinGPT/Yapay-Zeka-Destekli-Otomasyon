"""
Customer API Unit Tests
Tests for /api/customers endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, engine, Base
from app.models import Customer
from sqlalchemy.orm import Session

client = TestClient(app)

# Test data
TEST_CUSTOMER = {
    "name": "Test Müşteri A.Ş.",
    "name_en": "Test Customer Inc.",
    "email": "test@testmusteri.com",
    "phone": "+90 212 555 1234",
    "contact_person": "Ali Veli",
    "address": "Test Caddesi No:1",
    "city": "İstanbul",
    "country": "Türkiye",
    "tax_office": "Kadıköy",
    "tax_id": "1234567890",
    "notes": "Test müşteri"
}


def get_auth_header():
    """Get authentication header by logging in"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@betsan.com", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCustomerCreate:
    """Tests for POST /api/customers"""
    
    def test_create_customer_success(self):
        """Test successful customer creation"""
        headers = get_auth_header()
        response = client.post(
            "/api/customers/",
            json=TEST_CUSTOMER,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == TEST_CUSTOMER["name"]
        assert data["email"] == TEST_CUSTOMER["email"]
        assert data["is_active"] == True
        assert "id" in data
    
    def test_create_customer_unauthorized(self):
        """Test customer creation without auth"""
        response = client.post("/api/customers/", json=TEST_CUSTOMER)
        assert response.status_code == 401
    
    def test_create_customer_missing_name(self):
        """Test customer creation with missing required field"""
        headers = get_auth_header()
        invalid_data = {**TEST_CUSTOMER}
        del invalid_data["name"]
        response = client.post(
            "/api/customers/",
            json=invalid_data,
            headers=headers
        )
        assert response.status_code == 422


class TestCustomerRead:
    """Tests for GET /api/customers"""
    
    def test_get_customers_list(self):
        """Test getting list of customers"""
        headers = get_auth_header()
        response = client.get("/api/customers/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_customers_with_search(self):
        """Test customer search"""
        headers = get_auth_header()
        response = client.get(
            "/api/customers/?search=Test",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_customer_by_id(self):
        """Test getting a specific customer"""
        headers = get_auth_header()
        # First create a customer
        create_response = client.post(
            "/api/customers/",
            json={**TEST_CUSTOMER, "tax_id": "9999999999"},
            headers=headers
        )
        if create_response.status_code == 201:
            customer_id = create_response.json()["id"]
            
            # Get the customer
            response = client.get(f"/api/customers/{customer_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == customer_id
    
    def test_get_customer_not_found(self):
        """Test getting non-existent customer"""
        headers = get_auth_header()
        response = client.get("/api/customers/99999", headers=headers)
        assert response.status_code == 404


class TestCustomerUpdate:
    """Tests for PUT /api/customers/{id}"""
    
    def test_update_customer_success(self):
        """Test successful customer update"""
        headers = get_auth_header()
        # First create a customer
        create_response = client.post(
            "/api/customers/",
            json={**TEST_CUSTOMER, "tax_id": "8888888888"},
            headers=headers
        )
        if create_response.status_code == 201:
            customer_id = create_response.json()["id"]
            
            # Update the customer
            update_data = {"name": "Güncellenmiş Müşteri"}
            response = client.put(
                f"/api/customers/{customer_id}",
                json=update_data,
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["name"] == "Güncellenmiş Müşteri"


class TestCustomerDelete:
    """Tests for DELETE /api/customers/{id}"""
    
    def test_delete_customer_success(self):
        """Test successful customer deletion (soft delete)"""
        headers = get_auth_header()
        # First create a customer
        create_response = client.post(
            "/api/customers/",
            json={**TEST_CUSTOMER, "tax_id": "7777777777"},
            headers=headers
        )
        if create_response.status_code == 201:
            customer_id = create_response.json()["id"]
            
            # Delete the customer
            response = client.delete(f"/api/customers/{customer_id}", headers=headers)
            assert response.status_code == 200
            
            # Verify customer is deactivated
            get_response = client.get(f"/api/customers/{customer_id}", headers=headers)
            assert get_response.json()["is_active"] == False
