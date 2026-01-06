"""
Settings API Unit Tests
Tests for /api/settings endpoints
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


class TestAppSettings:
    """Tests for app settings endpoints"""
    
    def test_get_settings(self):
        """Test getting all settings"""
        headers = get_auth_header()
        response = client.get("/api/settings/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "company" in data
        assert "invoice_numbering" in data
        assert "default_currency" in data
    
    def test_update_settings(self):
        """Test updating settings (requires admin role)"""
        headers = get_auth_header()
        
        # First get current settings
        get_response = client.get("/api/settings/", headers=headers)
        current = get_response.json()
        
        # Update
        response = client.put(
            "/api/settings/",
            json={
                "company": current["company"],
                "invoice_numbering": current["invoice_numbering"],
                "default_currency": "TRY",
                "default_vat_rate": "20.00"
            },
            headers=headers
        )
        # Skip if user doesn't have admin role
        if response.status_code == 403:
            pytest.skip("User does not have admin role")
        assert response.status_code == 200


class TestCompanySettings:
    """Tests for company settings endpoints"""
    
    def test_get_company_settings(self):
        """Test getting company settings"""
        headers = get_auth_header()
        response = client.get("/api/settings/company", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "company_name" in data
    
    def test_update_company_settings(self):
        """Test updating company settings (requires admin role)"""
        headers = get_auth_header()
        
        response = client.put(
            "/api/settings/company",
            json={
                "company_name": "Test Şirketi A.Ş.",
                "company_name_en": "Test Company Inc.",
                "tax_office": "Kadıköy",
                "tax_id": "1234567890"
            },
            headers=headers
        )
        if response.status_code == 403:
            pytest.skip("User does not have admin role")
        assert response.status_code == 200


class TestInvoiceNumbering:
    """Tests for invoice numbering settings"""
    
    def test_get_invoice_numbering(self):
        """Test getting invoice numbering settings"""
        headers = get_auth_header()
        response = client.get("/api/settings/invoice-numbering", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "prefix" in data
        assert "padding" in data
    
    def test_update_invoice_numbering(self):
        """Test updating invoice numbering settings (requires admin role)"""
        headers = get_auth_header()
        
        response = client.put(
            "/api/settings/invoice-numbering",
            json={
                "prefix": "FTR",
                "year_format": "%Y",
                "separator": "-",
                "padding": 6,
                "next_number": 1
            },
            headers=headers
        )
        if response.status_code == 403:
            pytest.skip("User does not have admin role")
        assert response.status_code == 200


class TestReferenceData:
    """Tests for reference data endpoints"""
    
    def test_get_currencies(self):
        """Test getting available currencies"""
        headers = get_auth_header()
        response = client.get("/api/settings/currencies", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "currencies" in data
        assert "default" in data
        
        # Check TRY is in the list
        currency_codes = [c["code"] for c in data["currencies"]]
        assert "TRY" in currency_codes
        assert "USD" in currency_codes
        assert "EUR" in currency_codes
    
    def test_get_expense_types(self):
        """Test getting expense types"""
        headers = get_auth_header()
        response = client.get("/api/settings/expense-types", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "types" in data
        type_codes = [t["code"] for t in data["types"]]
        assert "TRAVEL" in type_codes
        assert "FOOD" in type_codes
    
    def test_get_warehouse_types(self):
        """Test getting warehouse types"""
        headers = get_auth_header()
        response = client.get("/api/settings/warehouse-types", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "types" in data
        type_codes = [t["code"] for t in data["types"]]
        assert "PHYSICAL" in type_codes
        assert "VIRTUAL" in type_codes
    
    def test_get_project_statuses(self):
        """Test getting project statuses"""
        headers = get_auth_header()
        response = client.get("/api/settings/project-statuses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "statuses" in data
        status_codes = [s["code"] for s in data["statuses"]]
        assert "WON" in status_codes
        assert "ENGINEERING" in status_codes
        assert "COMPLETED" in status_codes
    
    def test_get_invoice_statuses(self):
        """Test getting invoice statuses"""
        headers = get_auth_header()
        response = client.get("/api/settings/invoice-statuses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "statuses" in data
        status_codes = [s["code"] for s in data["statuses"]]
        assert "DRAFT" in status_codes
        assert "PAID" in status_codes
