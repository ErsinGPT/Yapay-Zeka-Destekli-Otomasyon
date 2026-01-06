"""
Warehouses Router
Handles physical and virtual (vehicle) warehouse management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models import Warehouse, WarehouseStock, Product
from app.schemas import (
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    WarehouseStockResponse
)
from app.routers.auth import get_current_user

router = APIRouter()

# Warehouse types
WAREHOUSE_TYPES = ["PHYSICAL", "VIRTUAL"]


@router.get("/", response_model=List[WarehouseResponse])
async def get_warehouses(
    warehouse_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all warehouses.
    Includes both physical warehouses and virtual vehicle depots.
    """
    query = db.query(Warehouse)
    
    if warehouse_type:
        query = query.filter(Warehouse.warehouse_type == warehouse_type)
    
    if is_active is not None:
        query = query.filter(Warehouse.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Warehouse.name.ilike(search_term),
                Warehouse.code.ilike(search_term),
                Warehouse.vehicle_plate.ilike(search_term)
            )
        )
    
    return query.all()


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create new warehouse.
    For virtual warehouses (vehicles), vehicle_plate is required.
    """
    # Validate warehouse type
    if warehouse.warehouse_type not in WAREHOUSE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz depo tipi. İzin verilen: {WAREHOUSE_TYPES}"
        )
    
    # Virtual warehouses require vehicle plate
    if warehouse.warehouse_type == "VIRTUAL" and not warehouse.vehicle_plate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Araç deposu için plaka zorunludur"
        )
    
    # Check code uniqueness
    existing = db.query(Warehouse).filter(Warehouse.code == warehouse.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Depo kodu '{warehouse.code}' zaten kullanılıyor"
        )
    
    db_warehouse = Warehouse(**warehouse.model_dump())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """Get warehouse details"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Depo bulunamadı"
        )
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update warehouse"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Depo bulunamadı"
        )
    
    update_data = warehouse_update.model_dump(exclude_unset=True)
    
    # Check code uniqueness if changing
    if "code" in update_data and update_data["code"] != warehouse.code:
        existing = db.query(Warehouse).filter(Warehouse.code == update_data["code"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Depo kodu '{update_data['code']}' zaten kullanılıyor"
            )
    
    for key, value in update_data.items():
        setattr(warehouse, key, value)
    
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: int,
    force: bool = Query(False, description="Force delete even if warehouse has stock"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete warehouse (soft delete)"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Depo bulunamadı"
        )
    
    # Check if warehouse has stock
    has_stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == warehouse_id,
        WarehouseStock.quantity > 0
    ).first()
    
    if has_stock:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stoğu olan depo silinemez. Zorla silmek için force=true kullanın."
            )
        # Force delete - clear stock records
        db.query(WarehouseStock).filter(WarehouseStock.warehouse_id == warehouse_id).delete()
    
    warehouse.is_active = False
    db.commit()


@router.get("/{warehouse_id}/stock", response_model=List[WarehouseStockResponse])
async def get_warehouse_stock(
    warehouse_id: int,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get stock levels for a specific warehouse.
    Returns all products with quantities in this warehouse.
    """
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Depo bulunamadı"
        )
    
    query = db.query(WarehouseStock).filter(WarehouseStock.warehouse_id == warehouse_id)
    
    stocks = query.all()
    
    result = []
    for stock in stocks:
        product = db.query(Product).filter(Product.id == stock.product_id).first()
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            if product:
                if (search_lower not in product.name.lower() and 
                    search_lower not in product.sku.lower()):
                    continue
            else:
                continue
        
        result.append({
            "id": stock.id,
            "warehouse_id": stock.warehouse_id,
            "product_id": stock.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity or Decimal("0"),
            "available_quantity": stock.quantity - (stock.reserved_quantity or Decimal("0"))
        })
    
    return result
