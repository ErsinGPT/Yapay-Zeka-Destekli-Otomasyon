"""
Products API Unit Tests
Tests for /api/products endpoints
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


class TestProductCategories:
    """Tests for /api/products/categories"""
    
    def test_get_categories(self):
        """Test getting product categories"""
        headers = get_auth_header()
        response = client.get("/api/products/categories", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_category(self):
        """Test creating a product category"""
        headers = get_auth_header()
        response = client.post(
            "/api/products/categories",
            json={"name": "Test Kategori", "description": "Test açıklama"},
            headers=headers
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Kategori"


class TestProductCRUD:
    """Tests for product CRUD operations"""
    
    def test_get_products_list(self):
        """Test getting list of products"""
        headers = get_auth_header()
        response = client.get("/api/products/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_products_with_search(self):
        """Test searching products"""
        headers = get_auth_header()
        response = client.get("/api/products/?search=test", headers=headers)
        assert response.status_code == 200
    
    def test_create_product(self):
        """Test creating a product"""
        headers = get_auth_header()
        import time
        sku = f"TEST-{int(time.time())}"
        
        response = client.post(
            "/api/products/",
            json={
                "sku": sku,
                "name": "Test Ürün",
                "barcode": "1234567890",
                "unit": "Adet",
                "cost": 100.50,
                "list_price": 150.00,
                "currency": "TRY"
            },
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == sku
        assert data["name"] == "Test Ürün"
        return data["id"]
    
    def test_create_product_duplicate_sku(self):
        """Test creating product with duplicate SKU fails"""
        headers = get_auth_header()
        # First create a product
        import time
        sku = f"DUP-{int(time.time())}"
        
        client.post(
            "/api/products/",
            json={"sku": sku, "name": "Original"},
            headers=headers
        )
        
        # Try to create another with same SKU
        response = client.post(
            "/api/products/",
            json={"sku": sku, "name": "Duplicate"},
            headers=headers
        )
        assert response.status_code == 400
    
    def test_get_product_by_id(self):
        """Test getting a specific product"""
        headers = get_auth_header()
        # Create a product first
        import time
        sku = f"GET-{int(time.time())}"
        
        create_response = client.post(
            "/api/products/",
            json={"sku": sku, "name": "Get Test"},
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        response = client.get(f"/api/products/{product_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == product_id
    
    def test_get_product_not_found(self):
        """Test getting non-existent product"""
        headers = get_auth_header()
        response = client.get("/api/products/99999", headers=headers)
        assert response.status_code == 404
    
    def test_update_product(self):
        """Test updating a product"""
        headers = get_auth_header()
        # Create a product first
        import time
        sku = f"UPD-{int(time.time())}"
        
        create_response = client.post(
            "/api/products/",
            json={"sku": sku, "name": "Update Test"},
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/products/{product_id}",
            json={"name": "Updated Name", "list_price": 200.00},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert float(response.json()["list_price"]) == 200.00


class TestProductBOM:
    """Tests for BOM (Bill of Materials) operations"""
    
    def test_get_empty_bom(self):
        """Test getting BOM for product without components"""
        headers = get_auth_header()
        # Create parent product
        import time
        sku = f"BOM-PARENT-{int(time.time())}"
        
        create_response = client.post(
            "/api/products/",
            json={"sku": sku, "name": "BOM Parent"},
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        response = client.get(f"/api/products/{product_id}/bom", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_bom(self):
        """Test creating BOM for a product"""
        headers = get_auth_header()
        import time
        ts = int(time.time())
        
        # Create parent product
        parent_response = client.post(
            "/api/products/",
            json={"sku": f"PARENT-{ts}", "name": "Parent Product"},
            headers=headers
        )
        parent_id = parent_response.json()["id"]
        
        # Create child products
        child1_response = client.post(
            "/api/products/",
            json={"sku": f"CHILD1-{ts}", "name": "Child 1"},
            headers=headers
        )
        child1_id = child1_response.json()["id"]
        
        child2_response = client.post(
            "/api/products/",
            json={"sku": f"CHILD2-{ts}", "name": "Child 2"},
            headers=headers
        )
        child2_id = child2_response.json()["id"]
        
        # Create BOM
        response = client.post(
            f"/api/products/{parent_id}/bom",
            json=[
                {"child_product_id": child1_id, "quantity": 2},
                {"child_product_id": child2_id, "quantity": 1}
            ],
            headers=headers
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_stock_check_non_bom(self):
        """Test stock check for non-BOM product"""
        headers = get_auth_header()
        import time
        sku = f"NONBOM-{int(time.time())}"
        
        create_response = client.post(
            "/api/products/",
            json={"sku": sku, "name": "Non-BOM Product"},
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        response = client.get(f"/api/products/{product_id}/stock-check", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_bom"] == False
        assert response.json()["can_produce"] == True
