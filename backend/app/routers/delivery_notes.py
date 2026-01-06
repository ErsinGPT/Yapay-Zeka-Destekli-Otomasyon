"""
Delivery Notes Router
Handles internal delivery notes (Dahili İrsaliye) for warehouse transfers
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models import (
    DeliveryNote, DeliveryNoteItem, Project, Warehouse, Product,
    WarehouseStock, StockMovement, MovementType, User
)
from app.schemas import (
    DeliveryNoteCreate, DeliveryNoteUpdate, DeliveryNoteResponse,
    DeliveryNoteItemCreate, DeliveryNoteItemResponse
)
from app.routers.auth import get_current_user

router = APIRouter()

# Delivery note statuses
DELIVERY_NOTE_STATUSES = ["PENDING", "IN_TRANSIT", "DELIVERED"]


def generate_note_number(db: Session) -> str:
    """Generate unique delivery note number"""
    year = datetime.now().year
    last_note = db.query(DeliveryNote).filter(
        DeliveryNote.note_number.like(f"DN-{year}-%")
    ).order_by(DeliveryNote.id.desc()).first()
    
    if last_note:
        last_num = int(last_note.note_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"DN-{year}-{new_num:04d}"


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


@router.get("/", response_model=List[DeliveryNoteResponse])
async def get_delivery_notes(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    from_warehouse_id: Optional[int] = None,
    to_warehouse_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get all delivery notes"""
    query = db.query(DeliveryNote)
    
    if project_id:
        query = query.filter(DeliveryNote.project_id == project_id)
    
    if status:
        query = query.filter(DeliveryNote.status == status)
    
    if from_warehouse_id:
        query = query.filter(DeliveryNote.from_warehouse_id == from_warehouse_id)
    
    if to_warehouse_id:
        query = query.filter(DeliveryNote.to_warehouse_id == to_warehouse_id)
    
    if search:
        query = query.filter(DeliveryNote.note_number.ilike(f"%{search}%"))
    
    notes = query.order_by(DeliveryNote.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for note in notes:
        project = db.query(Project).filter(Project.id == note.project_id).first()
        from_wh = db.query(Warehouse).filter(Warehouse.id == note.from_warehouse_id).first()
        to_wh = db.query(Warehouse).filter(Warehouse.id == note.to_warehouse_id).first()
        items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note.id).all()
        
        items_response = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items_response.append({
                "id": item.id,
                "delivery_note_id": item.delivery_note_id,
                "product_id": item.product_id,
                "product_name": product.name if product else None,
                "product_sku": product.sku if product else None,
                "quantity": item.quantity,
                "notes": item.notes
            })
        
        result.append({
            **note.__dict__,
            "items": items_response,
            "project_code": project.project_code if project else None,
            "from_warehouse_name": from_wh.name if from_wh else None,
            "to_warehouse_name": to_wh.name if to_wh else None
        })
    
    return result


@router.post("/", response_model=DeliveryNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_note(
    note_data: DeliveryNoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new delivery note with items"""
    # Validate project
    project = db.query(Project).filter(Project.id == note_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate warehouses
    from_wh = db.query(Warehouse).filter(Warehouse.id == note_data.from_warehouse_id).first()
    to_wh = db.query(Warehouse).filter(Warehouse.id == note_data.to_warehouse_id).first()
    
    if not from_wh:
        raise HTTPException(status_code=404, detail="Kaynak depo bulunamadı")
    if not to_wh:
        raise HTTPException(status_code=404, detail="Hedef depo bulunamadı")
    
    if note_data.from_warehouse_id == note_data.to_warehouse_id:
        raise HTTPException(status_code=400, detail="Kaynak ve hedef depo aynı olamaz")
    
    # Check stock availability for all items
    for item_data in note_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Ürün bulunamadı: ID {item_data.product_id}")
        
        stock = db.query(WarehouseStock).filter(
            WarehouseStock.warehouse_id == note_data.from_warehouse_id,
            WarehouseStock.product_id == item_data.product_id
        ).first()
        
        available = (stock.quantity - (stock.reserved_quantity or Decimal("0"))) if stock else Decimal("0")
        if available < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Yetersiz stok: {product.name}. Mevcut: {available}, Talep: {item_data.quantity}"
            )
    
    note_number = generate_note_number(db)
    
    # Create note
    db_note = DeliveryNote(
        note_number=note_number,
        project_id=note_data.project_id,
        from_warehouse_id=note_data.from_warehouse_id,
        to_warehouse_id=note_data.to_warehouse_id,
        status="PENDING",
        notes=note_data.notes
    )
    db.add(db_note)
    db.flush()
    
    # Create items
    for item_data in note_data.items:
        db_item = DeliveryNoteItem(
            delivery_note_id=db_note.id,
            **item_data.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_note)
    
    # Build response
    items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == db_note.id).all()
    items_response = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_response.append({
            "id": item.id,
            "delivery_note_id": item.delivery_note_id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": item.quantity,
            "notes": item.notes
        })
    
    return {
        **db_note.__dict__,
        "items": items_response,
        "project_code": project.project_code,
        "from_warehouse_name": from_wh.name,
        "to_warehouse_name": to_wh.name
    }


@router.get("/{note_id}", response_model=DeliveryNoteResponse)
async def get_delivery_note(note_id: int, db: Session = Depends(get_db)):
    """Get delivery note details"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    project = db.query(Project).filter(Project.id == note.project_id).first()
    from_wh = db.query(Warehouse).filter(Warehouse.id == note.from_warehouse_id).first()
    to_wh = db.query(Warehouse).filter(Warehouse.id == note.to_warehouse_id).first()
    items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note.id).all()
    
    items_response = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_response.append({
            "id": item.id,
            "delivery_note_id": item.delivery_note_id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": item.quantity,
            "notes": item.notes
        })
    
    return {
        **note.__dict__,
        "items": items_response,
        "project_code": project.project_code if project else None,
        "from_warehouse_name": from_wh.name if from_wh else None,
        "to_warehouse_name": to_wh.name if to_wh else None
    }


@router.put("/{note_id}", response_model=DeliveryNoteResponse)
async def update_delivery_note(
    note_id: int,
    note_update: DeliveryNoteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update delivery note (only notes field, only if PENDING)"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    if note.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen irsaliyeler güncellenebilir")
    
    update_data = note_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)
    
    project = db.query(Project).filter(Project.id == note.project_id).first()
    from_wh = db.query(Warehouse).filter(Warehouse.id == note.from_warehouse_id).first()
    to_wh = db.query(Warehouse).filter(Warehouse.id == note.to_warehouse_id).first()
    items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note.id).all()
    
    items_response = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_response.append({
            "id": item.id,
            "delivery_note_id": item.delivery_note_id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": item.quantity,
            "notes": item.notes
        })
    
    return {
        **note.__dict__,
        "items": items_response,
        "project_code": project.project_code if project else None,
        "from_warehouse_name": from_wh.name if from_wh else None,
        "to_warehouse_name": to_wh.name if to_wh else None
    }


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete delivery note (only if PENDING)"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    if note.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen irsaliyeler silinebilir")
    
    # Delete items first
    db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note_id).delete()
    db.delete(note)
    db.commit()


@router.post("/{note_id}/ship")
async def ship_delivery_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ship delivery note - deduct from source warehouse"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    if note.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen irsaliyeler sevk edilebilir")
    
    items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note_id).all()
    
    # Check and deduct stock from source warehouse
    for item in items:
        stock = db.query(WarehouseStock).filter(
            WarehouseStock.warehouse_id == note.from_warehouse_id,
            WarehouseStock.product_id == item.product_id
        ).first()
        
        available = (stock.quantity - (stock.reserved_quantity or Decimal("0"))) if stock else Decimal("0")
        if available < item.quantity:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Yetersiz stok: {product.name if product else 'Bilinmeyen'}. Mevcut: {available}"
            )
        
        stock.quantity -= item.quantity
    
    note.status = "IN_TRANSIT"
    note.shipped_at = datetime.utcnow()
    note.shipped_by = current_user.id
    
    db.commit()
    
    return {
        "message": "İrsaliye sevk edildi",
        "note_number": note.note_number,
        "status": note.status
    }


@router.post("/{note_id}/deliver")
async def deliver_delivery_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deliver delivery note - add to destination warehouse"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    if note.status != "IN_TRANSIT":
        raise HTTPException(status_code=400, detail="Sadece transit irsaliyeler teslim edilebilir")
    
    items = db.query(DeliveryNoteItem).filter(DeliveryNoteItem.delivery_note_id == note_id).all()
    
    # Add stock to destination warehouse and create movements
    for item in items:
        stock = get_or_create_warehouse_stock(db, note.to_warehouse_id, item.product_id)
        stock.quantity += item.quantity
        
        # Create movement record
        product = db.query(Product).filter(Product.id == item.product_id).first()
        movement = StockMovement(
            project_id=note.project_id,
            product_id=item.product_id,
            movement_type=MovementType.TRANSFER.value,
            from_warehouse_id=note.from_warehouse_id,
            to_warehouse_id=note.to_warehouse_id,
            quantity=item.quantity,
            unit_cost=product.cost if product else None,
            reference_type="delivery_note",
            reference_id=note.id,
            notes=f"İrsaliye: {note.note_number}",
            created_by=current_user.id
        )
        db.add(movement)
    
    note.status = "DELIVERED"
    note.delivered_at = datetime.utcnow()
    note.received_by = current_user.id
    
    db.commit()
    
    return {
        "message": "İrsaliye teslim edildi",
        "note_number": note.note_number,
        "status": note.status
    }


@router.get("/{note_id}/pdf")
async def get_delivery_note_pdf(note_id: int, db: Session = Depends(get_db)):
    """Get PDF for delivery note"""
    note = db.query(DeliveryNote).filter(DeliveryNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="İrsaliye bulunamadı")
    
    # TODO: Implement PDF generation with ReportLab
    return {
        "note_id": note_id,
        "note_number": note.note_number,
        "pdf_url": f"/uploads/delivery-notes/{note_id}.pdf"
    }
