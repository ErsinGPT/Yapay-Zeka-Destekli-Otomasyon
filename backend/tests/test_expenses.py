"""
Expenses API Unit Tests
Tests for /api/expenses endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
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
    
    # Create one
    import time
    ts = int(time.time())
    
    customer_response = client.post(
        "/api/customers/",
        json={"name": f"Expense Test Customer {ts}"},
        headers=headers
    )
    customer_id = customer_response.json()["id"] if customer_response.status_code == 201 else client.get("/api/customers/", headers=headers).json()[0]["id"]
    
    opp_response = client.post(
        "/api/opportunities/",
        json={"title": f"Expense Test Opp {ts}", "customer_id": customer_id, "expected_revenue": 5000},
        headers=headers
    )
    if opp_response.status_code == 201:
        opp_id = opp_response.json()["id"]
        won_response = client.post(f"/api/opportunities/{opp_id}/won", headers=headers)
        if won_response.status_code == 200:
            return won_response.json()["id"]
    
    return None


class TestExpenseTypes:
    """Tests for expense types endpoint"""
    
    def test_get_expense_types(self):
        """Test getting expense types"""
        headers = get_auth_header()
        response = client.get("/api/expenses/types", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert "TRAVEL" in data["types"]


class TestExpenseCRUD:
    """Tests for expense CRUD operations"""
    
    def test_get_expenses_list(self):
        """Test getting list of expenses"""
        headers = get_auth_header()
        response = client.get("/api/expenses/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_expense(self):
        """Test creating an expense"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "TRAVEL",
                    "amount": 250.00,
                    "currency": "TRY",
                    "description": "Test seyahat masrafı"
                },
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["expense_type"] == "TRAVEL"
            assert data["status"] == "PENDING"
            return data["id"]
    
    def test_create_expense_invalid_type(self):
        """Test creating expense with invalid type fails"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "INVALID_TYPE",
                    "amount": 100,
                    "description": "Test"
                },
                headers=headers
            )
            assert response.status_code == 400
    
    def test_get_expense_by_id(self):
        """Test getting a specific expense"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create expense
            create_response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "FOOD",
                    "amount": 75,
                    "description": "Yemek masrafı"
                },
                headers=headers
            )
            expense_id = create_response.json()["id"]
            
            response = client.get(f"/api/expenses/{expense_id}", headers=headers)
            assert response.status_code == 200
            assert response.json()["id"] == expense_id
    
    def test_update_expense(self):
        """Test updating an expense"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create expense
            create_response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "TRANSPORT",
                    "amount": 50,
                    "description": "Original"
                },
                headers=headers
            )
            expense_id = create_response.json()["id"]
            
            # Update it
            response = client.put(
                f"/api/expenses/{expense_id}",
                json={"amount": 75, "description": "Updated"},
                headers=headers
            )
            assert response.status_code == 200
            assert float(response.json()["amount"]) == 75


class TestExpenseApproval:
    """Tests for expense approval workflow"""
    
    def test_approve_expense(self):
        """Test approving an expense"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create expense
            create_response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "ACCOMMODATION",
                    "amount": 500,
                    "description": "Konaklama"
                },
                headers=headers
            )
            expense_id = create_response.json()["id"]
            
            # Approve it
            response = client.post(f"/api/expenses/{expense_id}/approve", headers=headers)
            assert response.status_code == 200
            assert "new_balance" in response.json()
    
    def test_reject_expense(self):
        """Test rejecting an expense"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            # Create expense
            create_response = client.post(
                "/api/expenses/",
                json={
                    "project_id": project_id,
                    "expense_type": "OTHER",
                    "amount": 1000,
                    "description": "Pahalı masraf"
                },
                headers=headers
            )
            expense_id = create_response.json()["id"]
            
            # Reject it
            response = client.post(
                f"/api/expenses/{expense_id}/reject",
                json={"rejection_reason": "Bütçe aşımı"},
                headers=headers
            )
            assert response.status_code == 200


class TestPersonnelAccount:
    """Tests for personnel account endpoints"""
    
    def test_get_personnel_account(self):
        """Test getting personnel account"""
        headers = get_auth_header()
        
        # Get current user ID from auth
        me_response = client.get("/api/users/me", headers=headers)
        if me_response.status_code == 200:
            user_id = me_response.json()["id"]
            
            response = client.get(f"/api/expenses/personnel/{user_id}/account", headers=headers)
            assert response.status_code == 200
            assert "balance" in response.json()
    
    def test_get_personnel_transactions(self):
        """Test getting personnel transactions"""
        headers = get_auth_header()
        
        me_response = client.get("/api/users/me", headers=headers)
        if me_response.status_code == 200:
            user_id = me_response.json()["id"]
            
            response = client.get(f"/api/expenses/personnel/{user_id}/transactions", headers=headers)
            assert response.status_code == 200
            assert isinstance(response.json(), list)
