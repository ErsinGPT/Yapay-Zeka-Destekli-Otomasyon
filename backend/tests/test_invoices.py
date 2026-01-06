"""
Invoices API Unit Tests
Tests for /api/invoices endpoints
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


def get_test_project_and_customer(headers):
    """Get or create a test project and customer"""
    # Get existing project
    projects = client.get("/api/projects/", headers=headers).json()
    if projects:
        project = projects[0]
        return project["id"], project["customer_id"]
    
    # Create customer
    import time
    ts = int(time.time())
    
    customer_response = client.post(
        "/api/customers/",
        json={"name": f"Invoice Test Customer {ts}"},
        headers=headers
    )
    if customer_response.status_code == 201:
        customer_id = customer_response.json()["id"]
    else:
        customers = client.get("/api/customers/", headers=headers).json()
        customer_id = customers[0]["id"]
    
    # Create opportunity and convert to project
    opp_response = client.post(
        "/api/opportunities/",
        json={
            "title": f"Invoice Test Opportunity {ts}",
            "customer_id": customer_id,
            "expected_revenue": 50000
        },
        headers=headers
    )
    if opp_response.status_code == 201:
        opp_id = opp_response.json()["id"]
        won_response = client.post(f"/api/opportunities/{opp_id}/won", headers=headers)
        if won_response.status_code == 200:
            return won_response.json()["id"], customer_id
    
    return None, None


class TestInvoiceCRUD:
    """Tests for invoice CRUD operations"""
    
    def test_get_invoices_list(self):
        """Test getting list of invoices"""
        headers = get_auth_header()
        response = client.get("/api/invoices/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_invoices_with_filters(self):
        """Test filtering invoices"""
        headers = get_auth_header()
        response = client.get("/api/invoices/?invoice_type=DOMESTIC&status=DRAFT", headers=headers)
        assert response.status_code == 200
    
    def test_create_domestic_invoice(self):
        """Test creating a domestic invoice"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "DOMESTIC",
                    "invoice_date": datetime.now().isoformat(),
                    "currency": "TRY",
                    "vat_rate": 20.00,
                    "items": [
                        {
                            "description": "Test Hizmet",
                            "quantity": 1,
                            "unit_price": 1000.00
                        }
                    ]
                },
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["invoice_type"] == "DOMESTIC"
            assert data["status"] == "DRAFT"
            return data["id"]
    
    def test_create_export_invoice(self):
        """Test creating an export invoice with GTIP and English descriptions"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "EXPORT",
                    "invoice_date": datetime.now().isoformat(),
                    "currency": "USD",
                    "vat_rate": 0,
                    "items": [
                        {
                            "description": "Otomasyon Panosu",
                            "description_en": "Automation Panel",
                            "gtip_code": "8537.10.91.00.00",
                            "quantity": 1,
                            "unit_price": 5000.00
                        }
                    ]
                },
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["invoice_type"] == "EXPORT"
    
    def test_create_export_without_gtip_fails(self):
        """Test export invoice without GTIP code fails"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "EXPORT",
                    "invoice_date": datetime.now().isoformat(),
                    "items": [
                        {
                            "description": "No GTIP",
                            "quantity": 1,
                            "unit_price": 1000.00
                        }
                    ]
                },
                headers=headers
            )
            assert response.status_code == 400


class TestInvoiceWorkflow:
    """Tests for invoice workflow operations"""
    
    def test_send_invoice(self):
        """Test sending an invoice"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            # Create invoice
            create_response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "DOMESTIC",
                    "invoice_date": datetime.now().isoformat(),
                    "items": [{"description": "Service", "quantity": 1, "unit_price": 500}]
                },
                headers=headers
            )
            invoice_id = create_response.json()["id"]
            
            # Send it
            response = client.post(f"/api/invoices/{invoice_id}/send", headers=headers)
            assert response.status_code == 200
            assert response.json()["status"] == "SENT"
    
    def test_mark_paid(self):
        """Test marking invoice as paid"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            # Create and send invoice
            create_response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "DOMESTIC",
                    "invoice_date": datetime.now().isoformat(),
                    "items": [{"description": "Paid Service", "quantity": 1, "unit_price": 750}]
                },
                headers=headers
            )
            invoice_id = create_response.json()["id"]
            
            # Mark as paid
            response = client.post(f"/api/invoices/{invoice_id}/mark-paid", headers=headers)
            assert response.status_code == 200
    
    def test_cancel_draft_invoice(self):
        """Test cancelling a draft invoice"""
        headers = get_auth_header()
        project_id, customer_id = get_test_project_and_customer(headers)
        
        if project_id and customer_id:
            # Create invoice
            create_response = client.post(
                "/api/invoices/",
                json={
                    "project_id": project_id,
                    "customer_id": customer_id,
                    "invoice_type": "DOMESTIC",
                    "invoice_date": datetime.now().isoformat(),
                    "items": [{"description": "Cancel Test", "quantity": 1, "unit_price": 100}]
                },
                headers=headers
            )
            invoice_id = create_response.json()["id"]
            
            # Cancel it
            response = client.post(f"/api/invoices/{invoice_id}/cancel", headers=headers)
            assert response.status_code == 200
