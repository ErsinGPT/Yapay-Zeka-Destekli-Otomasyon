"""
Invoices Router
Handles domestic and export invoice management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

router = APIRouter()

# Invoice types
INVOICE_TYPES = ["DOMESTIC", "EXPORT"]


@router.get("/")
async def get_invoices(db: Session = Depends(get_db)):
    """Get all invoices with filtering options"""
    # TODO: Implement with type filtering
    return []


@router.post("/")
async def create_invoice(db: Session = Depends(get_db)):
    """
    Create new invoice.
    For EXPORT type, GTIP codes and English descriptions are required.
    """
    # TODO: Implement with validation
    return {"message": "Invoice created", "id": 1}


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get invoice details"""
    # TODO: Implement
    return {"id": invoice_id}


@router.put("/{invoice_id}")
async def update_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Update invoice.
    Cannot update if project is INVOICED status (immutable).
    """
    # TODO: Implement with business rules
    return {"message": "Invoice updated"}


@router.post("/{invoice_id}/send")
async def send_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Send invoice via e-Fatura API.
    This is a pluggable interface - actual implementation depends on integrator.
    
    For EXPORT invoices:
    - Validates GTIP codes exist
    - Validates English descriptions exist
    - Sets VAT to 0% automatically
    """
    # TODO: Implement with e-Fatura integration interface
    return {"message": "Invoice sent", "status": "pending"}


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    """Generate and download invoice PDF"""
    # TODO: Implement PDF generation
    return {"pdf_url": f"/uploads/invoices/{invoice_id}.pdf"}
