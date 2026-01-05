"""
Project API Unit Tests
Tests for /api/projects endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_header():
    """Get authentication header by logging in"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@betsan.com", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_test_project(headers):
    """Helper to create a test project via opportunity flow"""
    # Create customer
    customer_response = client.post(
        "/api/customers/",
        json={"name": "Project Test Customer", "city": "İzmir"},
        headers=headers
    )
    if customer_response.status_code == 201:
        customer_id = customer_response.json()["id"]
    else:
        # Get existing
        list_resp = client.get("/api/customers/?search=Project Test", headers=headers)
        if list_resp.json():
            customer_id = list_resp.json()[0]["id"]
        else:
            return None
    
    # Create opportunity
    opp_response = client.post(
        "/api/opportunities/",
        json={
            "title": "Test Project Opportunity",
            "customer_id": customer_id,
            "expected_revenue": 75000
        },
        headers=headers
    )
    if opp_response.status_code == 201:
        opp_id = opp_response.json()["id"]
        
        # Mark as won to create project
        won_response = client.post(f"/api/opportunities/{opp_id}/won", headers=headers)
        if won_response.status_code == 200:
            return won_response.json()
    
    return None


class TestProjectRead:
    """Tests for GET /api/projects"""
    
    def test_get_projects_list(self):
        """Test getting list of projects"""
        headers = get_auth_header()
        response = client.get("/api/projects/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_projects_with_search(self):
        """Test searching projects"""
        headers = get_auth_header()
        response = client.get("/api/projects/?search=PRJ", headers=headers)
        assert response.status_code == 200
    
    def test_get_projects_with_status_filter(self):
        """Test filtering projects by status"""
        headers = get_auth_header()
        response = client.get("/api/projects/?status=WON", headers=headers)
        assert response.status_code == 200
    
    def test_get_project_by_id(self):
        """Test getting a specific project"""
        headers = get_auth_header()
        project = create_test_project(headers)
        if project:
            project_id = project["id"]
            response = client.get(f"/api/projects/{project_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == project_id
    
    def test_get_project_by_code(self):
        """Test getting a project by its code"""
        headers = get_auth_header()
        # Get any existing project
        list_response = client.get("/api/projects/", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            project_code = list_response.json()[0]["project_code"]
            response = client.get(f"/api/projects/code/{project_code}", headers=headers)
            assert response.status_code == 200
            assert response.json()["project_code"] == project_code
    
    def test_get_project_not_found(self):
        """Test getting non-existent project"""
        headers = get_auth_header()
        response = client.get("/api/projects/99999", headers=headers)
        assert response.status_code == 404


class TestProjectStatuses:
    """Tests for GET /api/projects/statuses"""
    
    def test_get_project_statuses(self):
        """Test getting available project statuses"""
        headers = get_auth_header()
        response = client.get("/api/projects/statuses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "statuses" in data
        assert "descriptions" in data
        assert len(data["statuses"]) == 10  # 10 Waterfall stages


class TestProjectUpdate:
    """Tests for PUT /api/projects/{id}"""
    
    def test_update_project_success(self):
        """Test successful project update"""
        headers = get_auth_header()
        # Get any existing project
        list_response = client.get("/api/projects/", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            project_id = list_response.json()[0]["id"]
            
            update_response = client.put(
                f"/api/projects/{project_id}",
                json={"notes": "Updated via test"},
                headers=headers
            )
            assert update_response.status_code == 200
            assert update_response.json()["notes"] == "Updated via test"


class TestProjectStatusUpdate:
    """Tests for PUT /api/projects/{id}/status"""
    
    def test_update_project_status_success(self):
        """Test successful project status update"""
        headers = get_auth_header()
        project = create_test_project(headers)
        if project:
            project_id = project["id"]
            
            # Update status to ENGINEERING
            response = client.put(
                f"/api/projects/{project_id}/status",
                json={"status": "ENGINEERING"},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == "ENGINEERING"
    
    def test_update_project_status_invalid(self):
        """Test project status update with invalid status"""
        headers = get_auth_header()
        # Get any existing project
        list_response = client.get("/api/projects/", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            project_id = list_response.json()[0]["id"]
            
            response = client.put(
                f"/api/projects/{project_id}/status",
                json={"status": "INVALID_STATUS"},
                headers=headers
            )
            assert response.status_code == 400


class TestProjectSummary:
    """Tests for GET /api/projects/{id}/summary"""
    
    def test_get_project_summary(self):
        """Test getting project profitability summary"""
        headers = get_auth_header()
        project = create_test_project(headers)
        if project:
            project_id = project["id"]
            
            response = client.get(f"/api/projects/{project_id}/summary", headers=headers)
            assert response.status_code == 200
            data = response.json()
            
            assert "project_code" in data
            assert "revenue" in data
            assert "material_cost" in data
            assert "net_profit" in data
            assert "profit_margin" in data
