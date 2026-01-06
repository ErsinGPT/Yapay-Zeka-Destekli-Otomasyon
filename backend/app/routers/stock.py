"""
Stock Router
Handles stock operations: transfers, reservations, movements
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models import (
    Product, Warehouse, WarehouseStock, StockMovement, StockReservation,
    Project, MovementType, ReservationStatus
)
from app.schemas import (
    StockTransferRequest, StockReservationCreate, StockReservationResponse,
    StockMovementCreate, StockMovementResponse
)
from app.routers.auth import get_current_user

router = APIRouter()


def get_or_create_warehouse_stock(db: Session, warehouse_id: int, product_id: int) -> WarehouseStock:
    """Get or create warehouse stock record"""
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == warehouse_id,
        WarehouseStock.product_id == product_id
    ).first()
    
    if not stock:
        stock = WarehouseStock(
            warehouse_id=warehouse_id,
            product_id=product_id,
            quantity=Decimal("0"),
            reserved_quantity=Decimal("0")
        )
        db.add(stock)
        db.flush()
    
    return stock


@router.get("/")
async def get_stock_summary(
    db: Session = Depends(get_db)
):
    """
    Get stock summary statistics.
    Returns totals for products, stock, low stock, and reservations.
    """
    # Total products with stock
    total_products = db.query(func.count(func.distinct(WarehouseStock.product_id))).scalar() or 0
    
    # Total stock quantity
    total_stock = db.query(func.sum(WarehouseStock.quantity)).scalar() or 0
    
    # Low stock count (products below min_stock_level)
    low_stock_count = 0
    products_with_stock = db.query(
        WarehouseStock.product_id,
        func.sum(WarehouseStock.quantity).label('total_qty')
    ).group_by(WarehouseStock.product_id).all()
    
    for ps in products_with_stock:
        product = db.query(Product).filter(Product.id == ps.product_id).first()
        if product and product.min_stock_level and ps.total_qty < product.min_stock_level:
            low_stock_count += 1
    
    # Reserved stock
    reserved_stock = db.query(func.sum(WarehouseStock.reserved_quantity)).scalar() or 0
    
    return {
        "total_products": total_products,
        "total_stock": float(total_stock),
        "low_stock_count": low_stock_count,
        "reserved_stock": float(reserved_stock)
    }


@router.post("/transfer")
async def transfer_stock(
    transfer: StockTransferRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Transfer stock between warehouses.
    Creates stock movements and updates stock levels.
    
    Business Rule: Warehouses cannot have negative balance.
    """
    # Validate project
    project = db.query(Project).filter(Project.id == transfer.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate product
    product = db.query(Product).filter(Product.id == transfer.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # Validate warehouses
    from_warehouse = db.query(Warehouse).filter(Warehouse.id == transfer.from_warehouse_id).first()
    to_warehouse = db.query(Warehouse).filter(Warehouse.id == transfer.to_warehouse_id).first()
    
    if not from_warehouse:
        raise HTTPException(status_code=404, detail="Kaynak depo bulunamadı")
    if not to_warehouse:
        raise HTTPException(status_code=404, detail="Hedef depo bulunamadı")
    
    if transfer.from_warehouse_id == transfer.to_warehouse_id:
        raise HTTPException(status_code=400, detail="Kaynak ve hedef depo aynı olamaz")
    
    # Check source stock
    from_stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == transfer.from_warehouse_id,
        WarehouseStock.product_id == transfer.product_id
    ).first()
    
    available = (from_stock.quantity - (from_stock.reserved_quantity or Decimal("0"))) if from_stock else Decimal("0")
    
    if available < transfer.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Yetersiz stok. Mevcut: {available}, Talep: {transfer.quantity}"
        )
    
    # Deduct from source
    from_stock.quantity -= transfer.quantity
    
    # Add to destination
    to_stock = get_or_create_warehouse_stock(db, transfer.to_warehouse_id, transfer.product_id)
    to_stock.quantity += transfer.quantity
    
    # Create movement record
    movement = StockMovement(
        project_id=transfer.project_id,
        product_id=transfer.product_id,
        movement_type=MovementType.TRANSFER.value,
        from_warehouse_id=transfer.from_warehouse_id,
        to_warehouse_id=transfer.to_warehouse_id,
        quantity=transfer.quantity,
        unit_cost=product.cost,
        notes=transfer.notes,
        created_by=current_user.id
    )
    db.add(movement)
    
    db.commit()
    db.refresh(movement)
    
    return {
        "message": "Transfer tamamlandı",
        "movement_id": movement.id,
        "from_warehouse": from_warehouse.name,
        "to_warehouse": to_warehouse.name,
        "product": product.name,
        "quantity": float(transfer.quantity)
    }


@router.post("/reserve", response_model=StockReservationResponse)
async def reserve_stock(
    reservation: StockReservationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Reserve stock for a project.
    Reserved stock is not available for other projects.
    """
    # Validate project
    project = db.query(Project).filter(Project.id == reservation.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate product
    product = db.query(Product).filter(Product.id == reservation.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # Check available stock
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == reservation.warehouse_id,
        WarehouseStock.product_id == reservation.product_id
    ).first()
    
    available = (stock.quantity - (stock.reserved_quantity or Decimal("0"))) if stock else Decimal("0")
    
    if available < reservation.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Yetersiz stok. Mevcut: {available}, Talep: {reservation.quantity}"
        )
    
    # Create reservation
    db_reservation = StockReservation(
        project_id=reservation.project_id,
        product_id=reservation.product_id,
        warehouse_id=reservation.warehouse_id,
        quantity=reservation.quantity,
        status=ReservationStatus.ACTIVE.value,
        notes=reservation.notes,
        created_by=current_user.id
    )
    db.add(db_reservation)
    
    # Update reserved quantity
    stock = get_or_create_warehouse_stock(db, reservation.warehouse_id, reservation.product_id)
    stock.reserved_quantity = (stock.reserved_quantity or Decimal("0")) + reservation.quantity
    
    db.commit()
    db.refresh(db_reservation)
    
    return db_reservation


@router.delete("/reserve/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel stock reservation"""
    reservation = db.query(StockReservation).filter(StockReservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı")
    
    if reservation.status != ReservationStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Sadece aktif rezervasyonlar iptal edilebilir")
    
    # Release reserved quantity
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == reservation.warehouse_id,
        WarehouseStock.product_id == reservation.product_id
    ).first()
    
    if stock:
        stock.reserved_quantity = max(Decimal("0"), (stock.reserved_quantity or Decimal("0")) - reservation.quantity)
    
    reservation.status = ReservationStatus.CANCELLED.value
    
    db.commit()
    
    return {"message": "Rezervasyon iptal edildi"}


@router.post("/reserve/{reservation_id}/fulfill")
async def fulfill_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Fulfill stock reservation - deduct from stock"""
    reservation = db.query(StockReservation).filter(StockReservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı")
    
    if reservation.status != ReservationStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail="Sadece aktif rezervasyonlar tamamlanabilir")
    
    # Deduct from stock
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.warehouse_id == reservation.warehouse_id,
        WarehouseStock.product_id == reservation.product_id
    ).first()
    
    if stock:
        stock.quantity -= reservation.quantity
        stock.reserved_quantity = max(Decimal("0"), (stock.reserved_quantity or Decimal("0")) - reservation.quantity)
    
    # Create movement record
    product = db.query(Product).filter(Product.id == reservation.product_id).first()
    movement = StockMovement(
        project_id=reservation.project_id,
        product_id=reservation.product_id,
        movement_type=MovementType.OUT.value,
        from_warehouse_id=reservation.warehouse_id,
        quantity=reservation.quantity,
        unit_cost=product.cost if product else None,
        reference_type="reservation",
        reference_id=reservation.id,
        notes=f"Rezervasyon tamamlama: {reservation.notes or ''}",
        created_by=current_user.id
    )
    db.add(movement)
    
    reservation.status = ReservationStatus.FULFILLED.value
    reservation.fulfilled_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Rezervasyon tamamlandı", "movement_id": movement.id}


@router.get("/movements", response_model=List[StockMovementResponse])
async def get_stock_movements(
    project_id: Optional[int] = None,
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get stock movement history.
    All movements must have a project_id (NOT NULL).
    """
    query = db.query(StockMovement)
    
    if project_id:
        query = query.filter(StockMovement.project_id == project_id)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    if warehouse_id:
        query = query.filter(
            or_(
                StockMovement.from_warehouse_id == warehouse_id,
                StockMovement.to_warehouse_id == warehouse_id
            )
        )
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    movements = query.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for mov in movements:
        product = db.query(Product).filter(Product.id == mov.product_id).first()
        from_warehouse = db.query(Warehouse).filter(Warehouse.id == mov.from_warehouse_id).first() if mov.from_warehouse_id else None
        to_warehouse = db.query(Warehouse).filter(Warehouse.id == mov.to_warehouse_id).first() if mov.to_warehouse_id else None
        
        result.append({
            "id": mov.id,
            "project_id": mov.project_id,
            "product_id": mov.product_id,
            "product_name": product.name if product else None,
            "movement_type": mov.movement_type,
            "from_warehouse_id": mov.from_warehouse_id,
            "from_warehouse_name": from_warehouse.name if from_warehouse else None,
            "to_warehouse_id": mov.to_warehouse_id,
            "to_warehouse_name": to_warehouse.name if to_warehouse else None,
            "quantity": mov.quantity,
            "unit_cost": mov.unit_cost,
            "reference_type": mov.reference_type,
            "reference_id": mov.reference_id,
            "notes": mov.notes,
            "created_at": mov.created_at
        })
    
    return result


@router.post("/movements", response_model=StockMovementResponse)
async def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create manual stock movement (IN, OUT, ADJUSTMENT)"""
    # Validate project only if provided
    if movement.project_id:
        project = db.query(Project).filter(Project.id == movement.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate product
    product = db.query(Product).filter(Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    # Process based on movement type
    if movement.movement_type == MovementType.IN.value:
        if not movement.to_warehouse_id:
            raise HTTPException(status_code=400, detail="Giriş için hedef depo zorunlu")
        stock = get_or_create_warehouse_stock(db, movement.to_warehouse_id, movement.product_id)
        stock.quantity += movement.quantity
        
    elif movement.movement_type == MovementType.OUT.value:
        if not movement.from_warehouse_id:
            raise HTTPException(status_code=400, detail="Çıkış için kaynak depo zorunlu")
        stock = db.query(WarehouseStock).filter(
            WarehouseStock.warehouse_id == movement.from_warehouse_id,
            WarehouseStock.product_id == movement.product_id
        ).first()
        if not stock or stock.quantity < movement.quantity:
            raise HTTPException(status_code=400, detail="Yetersiz stok")
        stock.quantity -= movement.quantity
        
    elif movement.movement_type == MovementType.ADJUSTMENT.value:
        warehouse_id = movement.to_warehouse_id or movement.from_warehouse_id
        if not warehouse_id:
            raise HTTPException(status_code=400, detail="Düzeltme için depo zorunlu")
        stock = get_or_create_warehouse_stock(db, warehouse_id, movement.product_id)
        # For adjustment, quantity can be positive (increase) or we use to/from to determine direction
        if movement.to_warehouse_id:
            stock.quantity += movement.quantity
        else:
            stock.quantity -= movement.quantity
    else:
        raise HTTPException(status_code=400, detail=f"Geçersiz hareket tipi: {movement.movement_type}")
    
    # Create movement record
    db_movement = StockMovement(
        project_id=movement.project_id,
        product_id=movement.product_id,
        movement_type=movement.movement_type,
        from_warehouse_id=movement.from_warehouse_id,
        to_warehouse_id=movement.to_warehouse_id,
        quantity=movement.quantity,
        unit_cost=movement.unit_cost or product.cost,
        notes=movement.notes,
        created_by=current_user.id
    )
    db.add(db_movement)
    
    db.commit()
    db.refresh(db_movement)
    
    return {
        "id": db_movement.id,
        "project_id": db_movement.project_id,
        "product_id": db_movement.product_id,
        "product_name": product.name,
        "movement_type": db_movement.movement_type,
        "from_warehouse_id": db_movement.from_warehouse_id,
        "to_warehouse_id": db_movement.to_warehouse_id,
        "quantity": db_movement.quantity,
        "unit_cost": db_movement.unit_cost,
        "reference_type": db_movement.reference_type,
        "reference_id": db_movement.reference_id,
        "notes": db_movement.notes,
        "created_at": db_movement.created_at
    }


@router.get("/check-availability")
async def check_availability(
    product_id: int,
    quantity: Decimal,
    warehouse_id: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Check if product is available in requested quantity.
    If project_id is provided, checks if it's reserved for another project.
    """
    query = db.query(WarehouseStock).filter(WarehouseStock.product_id == product_id)
    
    if warehouse_id:
        query = query.filter(WarehouseStock.warehouse_id == warehouse_id)
    
    stocks = query.all()
    
    total_available = Decimal("0")
    warehouses_with_stock = []
    
    for stock in stocks:
        available = stock.quantity - (stock.reserved_quantity or Decimal("0"))
        if available > 0:
            total_available += available
            warehouse = db.query(Warehouse).filter(Warehouse.id == stock.warehouse_id).first()
            warehouses_with_stock.append({
                "warehouse_id": stock.warehouse_id,
                "warehouse_name": warehouse.name if warehouse else None,
                "available": float(available)
            })
    
    # Check if reserved for another project
    reserved_for_other = None
    if project_id:
        other_reservations = db.query(StockReservation).filter(
            StockReservation.product_id == product_id,
            StockReservation.project_id != project_id,
            StockReservation.status == ReservationStatus.ACTIVE.value
        ).all()
        
        if other_reservations:
            reserved_for_other = [
                {"project_id": r.project_id, "quantity": float(r.quantity)}
                for r in other_reservations
            ]
    
    return {
        "product_id": product_id,
        "requested_quantity": float(quantity),
        "total_available": float(total_available),
        "available": total_available >= quantity,
        "warehouses": warehouses_with_stock,
        "reserved_for_other_projects": reserved_for_other,
        "warning": "Yetersiz stok" if total_available < quantity else None
    }
