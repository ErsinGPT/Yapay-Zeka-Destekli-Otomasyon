"""
Products Router
Handles product/stock card management and BOM operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

router = APIRouter()


@router.get("/")
async def get_products(db: Session = Depends(get_db)):
    """
    Get all products with stock information.
    Returns physical stock and available stock (after reservations).
    """
    # TODO: Implement with stock calculations
    return []


@router.post("/")
async def create_product(db: Session = Depends(get_db)):
    """Create new product/stock card"""
    # TODO: Implement
    return {"message": "Product created"}


@router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product with full details"""
    # TODO: Implement
    return {"id": product_id}


@router.put("/{product_id}")
async def update_product(product_id: int, db: Session = Depends(get_db)):
    """Update product"""
    # TODO: Implement
    return {"message": "Product updated"}


@router.get("/{product_id}/bom")
async def get_product_bom(product_id: int, db: Session = Depends(get_db)):
    """
    Get BOM (Bill of Materials) for a product.
    Returns list of child components with quantities.
    """
    # TODO: Implement BOM retrieval
    return {
        "parent_id": product_id,
        "components": []
    }


@router.post("/{product_id}/bom")
async def update_product_bom(product_id: int, db: Session = Depends(get_db)):
    """
    Create or update BOM for a product.
    Used for defining panel components (PLC, relays, etc.)
    """
    # TODO: Implement BOM creation
    return {"message": "BOM updated"}


@router.get("/{product_id}/barcode")
async def generate_barcode(product_id: int, db: Session = Depends(get_db)):
    """
    Generate barcode/QR code for product.
    Returns image URL.
    """
    # TODO: Implement barcode generation
    return {"barcode_url": f"/uploads/barcodes/{product_id}.png"}


@router.get("/{product_id}/stock-check")
async def check_bom_stock(product_id: int, db: Session = Depends(get_db)):
    """
    Check if all BOM components are available in stock.
    Returns availability status for each component.
    """
    # TODO: Implement BOM stock check
    return {
        "can_produce": True,
        "missing_components": []
    }
