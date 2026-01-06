"""
Service Forms API Unit Tests
Tests for /api/service-forms endpoints
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


def create_test_product(headers):
    """Create a test product"""
    import time
    sku = f"SF-PROD-{int(time.time())}"
    response = client.post(
        "/api/products/",
        json={"sku": sku, "name": "Service Form Test Product"},
        headers=headers
    )
    return response.json()["id"]


class TestServiceFormCRUD:
    """Tests for service form CRUD operations"""
    
    def test_get_service_forms_list(self):
        """Test getting list of service forms"""
        headers = get_auth_header()
        response = client.get("/api/service-forms/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_service_form(self):
        """Test creating a service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            response = client.post(
                "/api/service-forms/",
                json={
                    "project_id": project_id,
                    "work_description": "Test bakım işlemi",
                    "notes": "Test notları"
                },
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "OPEN"
            assert "form_number" in data
            return data["id"]
    
    def test_get_service_form_by_id(self):
        """Test getting a specific service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create form
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Get test"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            response = client.get(f"/api/service-forms/{form_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == form_id
    
    def test_update_service_form(self):
        """Test updating a service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create form
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Original"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            # Update it
            response = client.put(
                f"/api/service-forms/{form_id}",
                json={"work_description": "Updated", "notes": "New notes"},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["work_description"] == "Updated"
            # Status should change to IN_PROGRESS
            assert response.json()["status"] == "IN_PROGRESS"


class TestServiceFormMaterials:
    """Tests for service form material operations"""
    
    def test_add_material_to_form(self):
        """Test adding material to service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            product_id = create_test_product(headers)
            
            # Create form
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Material test"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            # Add material
            response = client.post(
                f"/api/service-forms/{form_id}/add-material",
                json={
                    "product_id": product_id,
                    "quantity": 2,
                    "delivered_to_customer": True,
                    "notes": "Test malzeme"
                },
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["product_id"] == product_id
    
    def test_remove_material_from_form(self):
        """Test removing material from service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            product_id = create_test_product(headers)
            
            # Create form and add material
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Remove test"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            add_response = client.post(
                f"/api/service-forms/{form_id}/add-material",
                json={"product_id": product_id, "quantity": 1},
                headers=headers
            )
            item_id = add_response.json()["id"]
            
            # Remove it
            response = client.delete(
                f"/api/service-forms/{form_id}/materials/{item_id}",
                headers=headers
            )
            assert response.status_code == 204


class TestServiceFormCompletion:
    """Tests for service form completion"""
    
    def test_complete_service_form(self):
        """Test completing a service form"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create form
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Complete test"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            # Complete it
            response = client.post(
                f"/api/service-forms/{form_id}/complete",
                json={
                    "work_performed": "İş tamamlandı",
                    "customer_name": "Müşteri Adı",
                    "customer_signed": True
                },
                headers=headers
            )
            assert response.status_code == 200
            assert "form_number" in response.json()
    
    def test_complete_already_completed_fails(self):
        """Test completing an already completed form fails"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create and complete form
            create_response = client.post(
                "/api/service-forms/",
                json={"project_id": project_id, "work_description": "Double complete"},
                headers=headers
            )
            form_id = create_response.json()["id"]
            
            client.post(
                f"/api/service-forms/{form_id}/complete",
                json={"work_performed": "Done", "customer_name": "Test", "customer_signed": True},
                headers=headers
            )
            
            # Try to complete again
            response = client.post(
                f"/api/service-forms/{form_id}/complete",
                json={"work_performed": "Again", "customer_name": "Test", "customer_signed": True},
                headers=headers
            )
            assert response.status_code == 400
