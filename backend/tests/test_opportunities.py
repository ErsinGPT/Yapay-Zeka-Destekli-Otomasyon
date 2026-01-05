"""
Opportunity API Unit Tests
Tests for /api/opportunities endpoints
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


def create_test_customer(headers):
    """Helper to create a test customer"""
    customer_data = {
        "name": f"Opportunity Test Customer",
        "email": "opp-test@test.com",
        "city": "Ankara"
    }
    response = client.post("/api/customers/", json=customer_data, headers=headers)
    if response.status_code == 201:
        return response.json()["id"]
    # If already exists, get from list
    list_response = client.get("/api/customers/?search=Opportunity Test", headers=headers)
    if list_response.status_code == 200 and list_response.json():
        return list_response.json()[0]["id"]
    return None


class TestOpportunityCreate:
    """Tests for POST /api/opportunities"""
    
    def test_create_opportunity_success(self):
        """Test successful opportunity creation"""
        headers = get_auth_header()
        customer_id = create_test_customer(headers)
        assert customer_id is not None
        
        opportunity_data = {
            "title": "Test Fırsatı 2026",
            "description": "Test opportunity description",
            "customer_id": customer_id,
            "expected_revenue": 50000.00,
            "currency": "TRY",
            "probability": 70
        }
        
        response = client.post(
            "/api/opportunities/",
            json=opportunity_data,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == opportunity_data["title"]
        assert data["status"] == "NEW"
        assert "id" in data
    
    def test_create_opportunity_unauthorized(self):
        """Test opportunity creation without auth"""
        response = client.post("/api/opportunities/", json={"title": "Test"})
        assert response.status_code == 401
    
    def test_create_opportunity_invalid_customer(self):
        """Test opportunity creation with non-existent customer"""
        headers = get_auth_header()
        opportunity_data = {
            "title": "Invalid Customer Opportunity",
            "customer_id": 99999
        }
        response = client.post(
            "/api/opportunities/",
            json=opportunity_data,
            headers=headers
        )
        assert response.status_code == 404


class TestOpportunityRead:
    """Tests for GET /api/opportunities"""
    
    def test_get_opportunities_list(self):
        """Test getting list of opportunities"""
        headers = get_auth_header()
        response = client.get("/api/opportunities/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_opportunities_with_status_filter(self):
        """Test filtering opportunities by status"""
        headers = get_auth_header()
        response = client.get(
            "/api/opportunities/?status=NEW",
            headers=headers
        )
        assert response.status_code == 200
    
    def test_get_opportunity_by_id(self):
        """Test getting a specific opportunity"""
        headers = get_auth_header()
        # Get list first
        list_response = client.get("/api/opportunities/", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            opp_id = list_response.json()[0]["id"]
            response = client.get(f"/api/opportunities/{opp_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == opp_id
    
    def test_get_opportunity_not_found(self):
        """Test getting non-existent opportunity"""
        headers = get_auth_header()
        response = client.get("/api/opportunities/99999", headers=headers)
        assert response.status_code == 404


class TestOpportunityUpdate:
    """Tests for PUT /api/opportunities/{id}"""
    
    def test_update_opportunity_success(self):
        """Test successful opportunity update"""
        headers = get_auth_header()
        customer_id = create_test_customer(headers)
        
        # Create opportunity
        create_response = client.post(
            "/api/opportunities/",
            json={
                "title": "Update Test Opportunity",
                "customer_id": customer_id,
                "probability": 50
            },
            headers=headers
        )
        if create_response.status_code == 201:
            opp_id = create_response.json()["id"]
            
            # Update
            update_response = client.put(
                f"/api/opportunities/{opp_id}",
                json={"probability": 80, "status": "QUALIFIED"},
                headers=headers
            )
            assert update_response.status_code == 200
            assert update_response.json()["probability"] == 80
            assert update_response.json()["status"] == "QUALIFIED"


class TestOpportunityWon:
    """Tests for POST /api/opportunities/{id}/won"""
    
    def test_mark_opportunity_won_creates_project(self):
        """Test that marking opportunity as won creates a project"""
        headers = get_auth_header()
        customer_id = create_test_customer(headers)
        
        # Create opportunity
        create_response = client.post(
            "/api/opportunities/",
            json={
                "title": "Won Test Opportunity",
                "customer_id": customer_id,
                "expected_revenue": 100000
            },
            headers=headers
        )
        if create_response.status_code == 201:
            opp_id = create_response.json()["id"]
            
            # Mark as won
            won_response = client.post(
                f"/api/opportunities/{opp_id}/won",
                headers=headers
            )
            assert won_response.status_code == 200
            data = won_response.json()
            
            # Should return a project
            assert "project_code" in data
            assert data["project_code"].startswith("PRJ-")
            assert data["status"] == "WON"


class TestOpportunityLost:
    """Tests for POST /api/opportunities/{id}/lost"""
    
    def test_mark_opportunity_lost(self):
        """Test marking opportunity as lost"""
        headers = get_auth_header()
        customer_id = create_test_customer(headers)
        
        # Create opportunity
        create_response = client.post(
            "/api/opportunities/",
            json={
                "title": "Lost Test Opportunity",
                "customer_id": customer_id
            },
            headers=headers
        )
        if create_response.status_code == 201:
            opp_id = create_response.json()["id"]
            
            # Mark as lost
            lost_response = client.post(
                f"/api/opportunities/{opp_id}/lost",
                headers=headers
            )
            assert lost_response.status_code == 200


class TestOpportunityQuotes:
    """Tests for quotes endpoints"""
    
    def test_create_and_get_quotes(self):
        """Test creating and getting quotes for an opportunity"""
        headers = get_auth_header()
        customer_id = create_test_customer(headers)
        
        # Create opportunity
        create_response = client.post(
            "/api/opportunities/",
            json={
                "title": "Quote Test Opportunity",
                "customer_id": customer_id
            },
            headers=headers
        )
        if create_response.status_code == 201:
            opp_id = create_response.json()["id"]
            
            # Create quote
            quote_data = {
                "subtotal": 10000,
                "discount": 500,
                "tax": 1710,
                "total": 11210,
                "currency": "TRY"
            }
            quote_response = client.post(
                f"/api/opportunities/{opp_id}/quotes",
                json=quote_data,
                headers=headers
            )
            assert quote_response.status_code == 201
            assert quote_response.json()["version"] == 1
            
            # Get quotes
            get_quotes_response = client.get(
                f"/api/opportunities/{opp_id}/quotes",
                headers=headers
            )
            assert get_quotes_response.status_code == 200
            assert len(get_quotes_response.json()) >= 1
