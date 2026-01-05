"""
Service Forms Router
Handles technical service forms and field operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

router = APIRouter()

# Service form statuses
SERVICE_FORM_STATUSES = ["OPEN", "IN_PROGRESS", "COMPLETED"]


@router.get("/")
async def get_service_forms(db: Session = Depends(get_db)):
    """Get all service forms"""
    # TODO: Implement with filtering
    return []


@router.post("/")
async def create_service_form(db: Session = Depends(get_db)):
    """
    Create new service form.
    Associates with project and vehicle warehouse.
    """
    # TODO: Implement
    return {"message": "Service form created", "id": 1}


@router.get("/{form_id}")
async def get_service_form(form_id: int, db: Session = Depends(get_db)):
    """Get service form details with used materials"""
    # TODO: Implement
    return {"id": form_id}


@router.put("/{form_id}")
async def update_service_form(form_id: int, db: Session = Depends(get_db)):
    """Update service form (add materials, notes, etc.)"""
    # TODO: Implement
    return {"message": "Service form updated"}


@router.post("/{form_id}/add-material")
async def add_material_to_form(form_id: int, db: Session = Depends(get_db)):
    """
    Add used material to service form.
    Does not deduct from stock yet - only records usage.
    """
    # TODO: Implement
    return {"message": "Material added"}


@router.post("/{form_id}/complete")
async def complete_service_form(form_id: int, db: Session = Depends(get_db)):
    """
    Complete service form and finalize stock movements.
    
    Business Rules:
    - Deducts all materials from vehicle warehouse
    - Materials marked as 'delivered_to_customer' leave inventory
    - Cannot complete if vehicle warehouse has insufficient stock
    """
    # TODO: Implement with stock deduction logic
    return {"message": "Service form completed"}


@router.get("/{form_id}/delivery-note")
async def get_delivery_note(form_id: int, db: Session = Depends(get_db)):
    """Get delivery note PDF for service form"""
    # TODO: Implement PDF generation
    return {"pdf_url": f"/uploads/delivery-notes/{form_id}.pdf"}
