"""
Delivery Notes API Unit Tests
Tests for /api/delivery-notes endpoints
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


def get_test_project(headers):
    """Get or create a test project"""
    projects = client.get("/api/projects/", headers=headers).json()
    if projects:
        return projects[0]["id"]
    return None


def create_test_product_with_stock(headers, warehouse_id, project_id):
    """Create a test product with stock"""
    import time
    sku = f"DN-PROD-{int(time.time())}"
    
    # Create product
    prod_response = client.post(
        "/api/products/",
        json={"sku": sku, "name": "Delivery Note Test Product"},
        headers=headers
    )
    product_id = prod_response.json()["id"]
    
    # Add stock
    client.post(
        "/api/stock/movements",
        json={
            "project_id": project_id,
            "product_id": product_id,
            "movement_type": "IN",
            "to_warehouse_id": warehouse_id,
            "quantity": 100
        },
        headers=headers
    )
    
    return product_id


def create_test_warehouses(headers):
    """Create source and destination warehouses"""
    import time
    ts = int(time.time())
    
    # Source warehouse
    source_response = client.post(
        "/api/warehouses/",
        json={"name": "Source", "code": f"SRC-{ts}", "warehouse_type": "PHYSICAL"},
        headers=headers
    )
    source_id = source_response.json()["id"]
    
    # Destination warehouse
    dest_response = client.post(
        "/api/warehouses/",
        json={"name": "Destination", "code": f"DST-{ts}", "warehouse_type": "PHYSICAL"},
        headers=headers
    )
    dest_id = dest_response.json()["id"]
    
    return source_id, dest_id


class TestDeliveryNoteCRUD:
    """Tests for delivery note CRUD operations"""
    
    def test_get_delivery_notes_list(self):
        """Test getting list of delivery notes"""
        headers = get_auth_header()
        response = client.get("/api/delivery-notes/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_delivery_note(self):
        """Test creating a delivery note"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            source_id, dest_id = create_test_warehouses(headers)
            product_id = create_test_product_with_stock(headers, source_id, project_id)
            
            response = client.post(
                "/api/delivery-notes/",
                json={
                    "project_id": project_id,
                    "from_warehouse_id": source_id,
                    "to_warehouse_id": dest_id,
                    "notes": "Test irsaliyesi",
                    "items": [
                        {"product_id": product_id, "quantity": 10}
                    ]
                },
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "PENDING"
            assert "note_number" in data
            return data["id"]
    
    def test_create_delivery_note_same_warehouse_fails(self):
        """Test creating delivery note with same source and dest fails"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            source_id, _ = create_test_warehouses(headers)
            product_id = create_test_product_with_stock(headers, source_id, project_id)
            
            response = client.post(
                "/api/delivery-notes/",
                json={
                    "project_id": project_id,
                    "from_warehouse_id": source_id,
                    "to_warehouse_id": source_id,  # Same!
                    "items": [{"product_id": product_id, "quantity": 5}]
                },
                headers=headers
            )
            assert response.status_code == 400
    
    def test_get_delivery_note_by_id(self):
        """Test getting a specific delivery note"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if not project_id:
            pytest.skip("No test project available")
        
        source_id, dest_id = create_test_warehouses(headers)
        product_id = create_test_product_with_stock(headers, source_id, project_id)
        
        create_response = client.post(
            "/api/delivery-notes/",
            json={
                "project_id": project_id,
                "from_warehouse_id": source_id,
                "to_warehouse_id": dest_id,
                "items": [{"product_id": product_id, "quantity": 5}]
            },
            headers=headers
        )
        if create_response.status_code != 201:
            pytest.skip(f"Could not create delivery note: {create_response.json()}")
        note_id = create_response.json()["id"]
        
        response = client.get(f"/api/delivery-notes/{note_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == note_id


class TestDeliveryNoteWorkflow:
    """Tests for delivery note ship/deliver workflow"""
    
    def test_ship_delivery_note(self):
        """Test shipping a delivery note"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if not project_id:
            pytest.skip("No test project available")
        
        source_id, dest_id = create_test_warehouses(headers)
        product_id = create_test_product_with_stock(headers, source_id, project_id)
        
        create_response = client.post(
            "/api/delivery-notes/",
            json={
                "project_id": project_id,
                "from_warehouse_id": source_id,
                "to_warehouse_id": dest_id,
                "items": [{"product_id": product_id, "quantity": 10}]
            },
            headers=headers
        )
        if create_response.status_code != 201:
            pytest.skip(f"Could not create delivery note: {create_response.json()}")
        note_id = create_response.json()["id"]
        
        # Ship it
        response = client.post(f"/api/delivery-notes/{note_id}/ship", headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "IN_TRANSIT"
    
    def test_deliver_delivery_note(self):
        """Test delivering a shipped delivery note"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            source_id, dest_id = create_test_warehouses(headers)
            product_id = create_test_product_with_stock(headers, source_id, project_id)
            
            # Create
            create_response = client.post(
                "/api/delivery-notes/",
                json={
                    "project_id": project_id,
                    "from_warehouse_id": source_id,
                    "to_warehouse_id": dest_id,
                    "items": [{"product_id": product_id, "quantity": 5}]
                },
                headers=headers
            )
            note_id = create_response.json()["id"]
            
            # Ship
            client.post(f"/api/delivery-notes/{note_id}/ship", headers=headers)
            
            # Deliver
            response = client.post(f"/api/delivery-notes/{note_id}/deliver", headers=headers)
            assert response.status_code == 200
            assert response.json()["status"] == "DELIVERED"
    
    def test_deliver_pending_fails(self):
        """Test delivering a pending (not shipped) note fails"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if not project_id:
            pytest.skip("No test project available")
        
        source_id, dest_id = create_test_warehouses(headers)
        product_id = create_test_product_with_stock(headers, source_id, project_id)
        
        create_response = client.post(
            "/api/delivery-notes/",
            json={
                "project_id": project_id,
                "from_warehouse_id": source_id,
                "to_warehouse_id": dest_id,
                "items": [{"product_id": product_id, "quantity": 3}]
            },
            headers=headers
        )
        if create_response.status_code != 201:
            pytest.skip(f"Could not create delivery note: {create_response.json()}")
        note_id = create_response.json()["id"]
        
        # Try to deliver without shipping
        response = client.post(f"/api/delivery-notes/{note_id}/deliver", headers=headers)
        assert response.status_code == 400
    
    def test_delete_pending_note(self):
        """Test deleting a pending delivery note"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if not project_id:
            pytest.skip("No test project available")
        
        source_id, dest_id = create_test_warehouses(headers)
        product_id = create_test_product_with_stock(headers, source_id, project_id)
        
        create_response = client.post(
            "/api/delivery-notes/",
            json={
                "project_id": project_id,
                "from_warehouse_id": source_id,
                "to_warehouse_id": dest_id,
                "items": [{"product_id": product_id, "quantity": 2}]
            },
            headers=headers
        )
        if create_response.status_code != 201:
            pytest.skip(f"Could not create: {create_response.json()}")
        note_id = create_response.json()["id"]
        
        response = client.delete(f"/api/delivery-notes/{note_id}", headers=headers)
        assert response.status_code == 204
    
    def test_delete_shipped_note_fails(self):
        """Test deleting a shipped delivery note fails"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            source_id, dest_id = create_test_warehouses(headers)
            product_id = create_test_product_with_stock(headers, source_id, project_id)
            
            create_response = client.post(
                "/api/delivery-notes/",
                json={
                    "project_id": project_id,
                    "from_warehouse_id": source_id,
                    "to_warehouse_id": dest_id,
                    "items": [{"product_id": product_id, "quantity": 2}]
                },
                headers=headers
            )
            note_id = create_response.json()["id"]
            
            # Ship it
            client.post(f"/api/delivery-notes/{note_id}/ship", headers=headers)
            
            # Try to delete
            response = client.delete(f"/api/delivery-notes/{note_id}", headers=headers)
            assert response.status_code == 400
