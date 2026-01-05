"""
Stock Router
Handles stock operations: transfers, reservations, movements
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

router = APIRouter()


@router.get("/")
async def get_stock_summary(db: Session = Depends(get_db)):
    """
    Get total stock summary.
    Returns physical stock and available stock (after reservations).
    """
    # TODO: Implement
    return []


@router.post("/transfer")
async def transfer_stock(db: Session = Depends(get_db)):
    """
    Transfer stock between warehouses.
    Creates delivery note (Dahili İrsaliye) automatically.
    
    Business Rule: Virtual depots cannot have negative balance.
    """
    # TODO: Implement transfer logic
    return {
        "message": "Transfer completed",
        "delivery_note_id": 1
    }


@router.post("/reserve")
async def reserve_stock(db: Session = Depends(get_db)):
    """
    Reserve stock for a project.
    Reserved stock is not available for other projects.
    """
    # TODO: Implement reservation logic
    return {"message": "Stock reserved", "reservation_id": 1}


@router.delete("/reserve/{reservation_id}")
async def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """Cancel stock reservation"""
    # TODO: Implement
    return {"message": "Reservation cancelled"}


@router.get("/movements")
async def get_stock_movements(db: Session = Depends(get_db)):
    """
    Get stock movement history.
    All movements must have a project_id (NOT NULL).
    """
    # TODO: Implement with filtering
    return []


@router.get("/check-availability")
async def check_availability(
    product_id: int,
    quantity: int,
    project_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Check if product is available in requested quantity.
    If project_id is provided, checks if it's reserved for another project.
    """
    # TODO: Implement availability check
    return {
        "available": True,
        "reserved_for_project": None,
        "warning": None
    }
