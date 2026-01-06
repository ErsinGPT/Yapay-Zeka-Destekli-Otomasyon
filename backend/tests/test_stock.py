"""
Stock API Unit Tests
Tests for /api/stock endpoints
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


def create_test_product(headers):
    """Helper to create a test product"""
    import time
    sku = f"STOCK-{int(time.time())}"
    response = client.post(
        "/api/products/",
        json={"sku": sku, "name": "Stock Test Product"},
        headers=headers
    )
    return response.json()["id"]


def create_test_warehouse(headers):
    """Helper to create a test warehouse"""
    import time
    code = f"STOCKWH-{int(time.time())}"
    response = client.post(
        "/api/warehouses/",
        json={"name": "Stock Test Warehouse", "code": code, "warehouse_type": "PHYSICAL"},
        headers=headers
    )
    return response.json()["id"]


def create_test_project(headers):
    """Helper to create a test project"""
    # Create customer first
    import time
    ts = int(time.time())
    
    customer_response = client.post(
        "/api/customers/",
        json={"name": f"Stock Test Customer {ts}"},
        headers=headers
    )
    if customer_response.status_code != 201:
        # Get existing
        list_resp = client.get("/api/customers/", headers=headers)
        customer_id = list_resp.json()[0]["id"]
    else:
        customer_id = customer_response.json()["id"]
    
    # Create opportunity
    opp_response = client.post(
        "/api/opportunities/",
        json={
            "title": f"Stock Test Opportunity {ts}",
            "customer_id": customer_id,
            "expected_revenue": 10000
        },
        headers=headers
    )
    if opp_response.status_code == 201:
        opp_id = opp_response.json()["id"]
        # Mark as won
        won_response = client.post(f"/api/opportunities/{opp_id}/won", headers=headers)
        if won_response.status_code == 200:
            return won_response.json()["id"]
    
    # Fallback: get existing project
    projects = client.get("/api/projects/", headers=headers).json()
    if projects:
        return projects[0]["id"]
    return None


class TestStockSummary:
    """Tests for stock summary endpoint"""
    
    def test_get_stock_summary(self):
        """Test getting stock summary"""
        headers = get_auth_header()
        response = client.get("/api/stock/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_stock_summary_with_filter(self):
        """Test getting stock summary with filters"""
        headers = get_auth_header()
        response = client.get("/api/stock/?product_id=1", headers=headers)
        assert response.status_code == 200


class TestStockMovements:
    """Tests for stock movement operations"""
    
    def test_get_stock_movements(self):
        """Test getting stock movements"""
        headers = get_auth_header()
        response = client.get("/api/stock/movements", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_stock_in_movement(self):
        """Test creating stock IN movement"""
        headers = get_auth_header()
        
        product_id = create_test_product(headers)
        warehouse_id = create_test_warehouse(headers)
        project_id = create_test_project(headers)
        
        if project_id:
            response = client.post(
                "/api/stock/movements",
                json={
                    "project_id": project_id,
                    "product_id": product_id,
                    "movement_type": "IN",
                    "to_warehouse_id": warehouse_id,
                    "quantity": 100,
                    "notes": "Test girişi"
                },
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["movement_type"] == "IN"


class TestStockReservation:
    """Tests for stock reservation operations"""
    
    def test_create_and_cancel_reservation(self):
        """Test creating and cancelling a reservation"""
        headers = get_auth_header()
        
        product_id = create_test_product(headers)
        warehouse_id = create_test_warehouse(headers)
        project_id = create_test_project(headers)
        
        if project_id:
            # First add some stock
            client.post(
                "/api/stock/movements",
                json={
                    "project_id": project_id,
                    "product_id": product_id,
                    "movement_type": "IN",
                    "to_warehouse_id": warehouse_id,
                    "quantity": 50
                },
                headers=headers
            )
            
            # Create reservation
            reserve_response = client.post(
                "/api/stock/reserve",
                json={
                    "project_id": project_id,
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "quantity": 10
                },
                headers=headers
            )
            assert reserve_response.status_code == 200
            reservation_id = reserve_response.json()["id"]
            
            # Cancel reservation
            cancel_response = client.delete(
                f"/api/stock/reserve/{reservation_id}",
                headers=headers
            )
            assert cancel_response.status_code == 200


class TestStockAvailability:
    """Tests for stock availability check"""
    
    def test_check_availability(self):
        """Test checking stock availability"""
        headers = get_auth_header()
        
        product_id = create_test_product(headers)
        
        response = client.get(
            f"/api/stock/check-availability?product_id={product_id}&quantity=10",
            headers=headers
        )
        assert response.status_code == 200
        assert "available" in response.json()
        assert "total_available" in response.json()
