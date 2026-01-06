"""
Reports API Unit Tests
Tests for /api/reports endpoints
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
    """Get an existing project"""
    projects = client.get("/api/projects/", headers=headers).json()
    if projects:
        return projects[0]["id"]
    return None


class TestDashboard:
    """Tests for dashboard endpoint"""
    
    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        headers = get_auth_header()
        response = client.get("/api/reports/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total_projects" in data
        assert "active_projects" in data
        assert "total_revenue" in data
        assert "total_expenses" in data
        assert "pending_invoices" in data
        assert "low_stock_items" in data


class TestProjectProfitability:
    """Tests for project profitability report"""
    
    def test_get_project_profitability(self):
        """Test getting project profitability report"""
        headers = get_auth_header()
        project_id = get_test_project(headers)
        
        if project_id:
            response = client.get(
                f"/api/reports/project-profitability/{project_id}",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            
            assert "project_id" in data
            assert "revenue" in data
            assert "costs" in data
            assert "profit" in data
            assert "margin_percent" in data
    
    def test_get_project_profitability_not_found(self):
        """Test profitability for non-existent project"""
        headers = get_auth_header()
        response = client.get("/api/reports/project-profitability/99999", headers=headers)
        assert response.status_code == 404


class TestStockStatus:
    """Tests for stock status report"""
    
    def test_get_stock_status(self):
        """Test getting stock status report"""
        headers = get_auth_header()
        response = client.get("/api/reports/stock-status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "warehouses" in data
        assert "low_stock_alerts" in data
        assert "reserved_items" in data


class TestExpenseSummary:
    """Tests for expense summary report"""
    
    def test_get_expense_summary(self):
        """Test getting expense summary"""
        headers = get_auth_header()
        response = client.get("/api/reports/expense-summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "by_project" in data
        assert "by_type" in data
        assert "by_personnel" in data
    
    def test_get_expense_summary_with_dates(self):
        """Test expense summary with date filters"""
        headers = get_auth_header()
        response = client.get(
            "/api/reports/expense-summary?start_date=2024-01-01&end_date=2024-12-31",
            headers=headers
        )
        assert response.status_code == 200


class TestRevenueSummary:
    """Tests for revenue summary report"""
    
    def test_get_revenue_summary(self):
        """Test getting revenue summary"""
        headers = get_auth_header()
        response = client.get("/api/reports/revenue-summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "by_project" in data
        assert "by_month" in data


class TestCurrencyRates:
    """Tests for currency rates endpoint"""
    
    def test_get_currency_rates(self):
        """Test getting currency rates"""
        headers = get_auth_header()
        response = client.get("/api/reports/currency-rates", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "rates" in data
        assert "last_updated" in data


class TestOpportunitiesPipeline:
    """Tests for opportunities pipeline"""
    
    def test_get_opportunities_pipeline(self):
        """Test getting opportunities pipeline"""
        headers = get_auth_header()
        response = client.get("/api/reports/opportunities-pipeline", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "pipeline" in data
        assert "won" in data
        assert "lost" in data
        assert "win_rate" in data
