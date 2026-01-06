"""
Warehouses API Unit Tests
Tests for /api/warehouses endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_header():
    """Get authentication header by logging in"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@otomasyon.com", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestWarehouseCRUD:
    """Tests for warehouse CRUD operations"""
    
    def test_get_warehouses_list(self):
        """Test getting list of warehouses"""
        headers = get_auth_header()
        response = client.get("/api/warehouses/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_physical_warehouse(self):
        """Test creating a physical warehouse"""
        headers = get_auth_header()
        import time
        code = f"DEPO-{int(time.time())}"
        
        response = client.post(
            "/api/warehouses/",
            json={
                "name": "Test Deposu",
                "code": code,
                "warehouse_type": "PHYSICAL",
                "address": "Test Adres"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == code
        assert data["warehouse_type"] == "PHYSICAL"
        return data["id"]
    
    def test_create_virtual_warehouse(self):
        """Test creating a virtual (vehicle) warehouse"""
        headers = get_auth_header()
        import time
        code = f"ARAC-{int(time.time())}"
        
        response = client.post(
            "/api/warehouses/",
            json={
                "name": "Test Aracı",
                "code": code,
                "warehouse_type": "VIRTUAL",
                "vehicle_plate": "34 AB 123"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["warehouse_type"] == "VIRTUAL"
        assert data["vehicle_plate"] == "34 AB 123"
    
    def test_create_virtual_without_plate_fails(self):
        """Test creating virtual warehouse without plate fails"""
        headers = get_auth_header()
        import time
        code = f"FAIL-{int(time.time())}"
        
        response = client.post(
            "/api/warehouses/",
            json={
                "name": "No Plate Vehicle",
                "code": code,
                "warehouse_type": "VIRTUAL"
            },
            headers=headers
        )
        assert response.status_code == 400
    
    def test_create_warehouse_duplicate_code(self):
        """Test creating warehouse with duplicate code fails"""
        headers = get_auth_header()
        import time
        code = f"DUPCODE-{int(time.time())}"
        
        # First create
        client.post(
            "/api/warehouses/",
            json={"name": "Original", "code": code, "warehouse_type": "PHYSICAL"},
            headers=headers
        )
        
        # Try duplicate
        response = client.post(
            "/api/warehouses/",
            json={"name": "Duplicate", "code": code, "warehouse_type": "PHYSICAL"},
            headers=headers
        )
        assert response.status_code == 400
    
    def test_get_warehouse_by_id(self):
        """Test getting a specific warehouse"""
        headers = get_auth_header()
        import time
        code = f"GETID-{int(time.time())}"
        
        create_response = client.post(
            "/api/warehouses/",
            json={"name": "Get Test", "code": code, "warehouse_type": "PHYSICAL"},
            headers=headers
        )
        warehouse_id = create_response.json()["id"]
        
        response = client.get(f"/api/warehouses/{warehouse_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == warehouse_id
    
    def test_get_warehouse_not_found(self):
        """Test getting non-existent warehouse"""
        headers = get_auth_header()
        response = client.get("/api/warehouses/99999", headers=headers)
        assert response.status_code == 404
    
    def test_update_warehouse(self):
        """Test updating a warehouse"""
        headers = get_auth_header()
        import time
        code = f"UPDATE-{int(time.time())}"
        
        create_response = client.post(
            "/api/warehouses/",
            json={"name": "Update Test", "code": code, "warehouse_type": "PHYSICAL"},
            headers=headers
        )
        warehouse_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/warehouses/{warehouse_id}",
            json={"name": "Updated Name", "address": "New Address"},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    def test_get_warehouse_stock_empty(self):
        """Test getting stock for empty warehouse"""
        headers = get_auth_header()
        import time
        code = f"EMPTY-{int(time.time())}"
        
        create_response = client.post(
            "/api/warehouses/",
            json={"name": "Empty Warehouse", "code": code, "warehouse_type": "PHYSICAL"},
            headers=headers
        )
        warehouse_id = create_response.json()["id"]
        
        response = client.get(f"/api/warehouses/{warehouse_id}/stock", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
