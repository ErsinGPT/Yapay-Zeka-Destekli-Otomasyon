"""
Service Forms Router
Handles technical service forms and field operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models import (
    ServiceForm, ServiceFormItem, Project, Warehouse, Product,
    WarehouseStock, StockMovement, MovementType, User
)
from app.schemas import (
    ServiceFormCreate, ServiceFormUpdate, ServiceFormResponse,
    ServiceFormItemCreate, ServiceFormItemResponse, ServiceFormComplete
)
from app.routers.auth import get_current_user

router = APIRouter()

# Service form statuses
SERVICE_FORM_STATUSES = ["OPEN", "IN_PROGRESS", "COMPLETED"]


def generate_form_number(db: Session) -> str:
    """Generate unique form number"""
    year = datetime.now().year
    last_form = db.query(ServiceForm).filter(
        ServiceForm.form_number.like(f"SF-{year}-%")
    ).order_by(ServiceForm.id.desc()).first()
    
    if last_form:
        last_num = int(last_form.form_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"SF-{year}-{new_num:04d}"


@router.get("/", response_model=List[ServiceFormResponse])
async def get_service_forms(
    project_id: Optional[int] = None,
    technician_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get all service forms"""
    query = db.query(ServiceForm)
    
    if project_id:
        query = query.filter(ServiceForm.project_id == project_id)
    
    if technician_id:
        query = query.filter(ServiceForm.technician_id == technician_id)
    
    if status:
        query = query.filter(ServiceForm.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ServiceForm.form_number.ilike(search_term),
                ServiceForm.work_description.ilike(search_term)
            )
        )
    
    forms = query.order_by(ServiceForm.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for form in forms:
        project = db.query(Project).filter(Project.id == form.project_id).first()
        technician = db.query(User).filter(User.id == form.technician_id).first()
        items = db.query(ServiceFormItem).filter(ServiceFormItem.service_form_id == form.id).all()
        
        items_response = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items_response.append({
                "id": item.id,
                "service_form_id": item.service_form_id,
                "product_id": item.product_id,
                "product_name": product.name if product else None,
                "product_sku": product.sku if product else None,
                "quantity": item.quantity,
                "delivered_to_customer": item.delivered_to_customer,
                "notes": item.notes
            })
        
        result.append({
            **form.__dict__,
            "items": items_response,
            "project_code": project.project_code if project else None,
            "technician_name": technician.full_name if technician else None
        })
    
    return result


@router.post("/", response_model=ServiceFormResponse, status_code=status.HTTP_201_CREATED)
async def create_service_form(
    form_data: ServiceFormCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create new service form.
    Associates with project and vehicle warehouse.
    """
    # Validate project
    project = db.query(Project).filter(Project.id == form_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate vehicle warehouse if provided
    if form_data.vehicle_warehouse_id:
        warehouse = db.query(Warehouse).filter(
            Warehouse.id == form_data.vehicle_warehouse_id,
            Warehouse.warehouse_type == "VIRTUAL"
        ).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Araç deposu bulunamadı")
    
    form_number = generate_form_number(db)
    
    db_form = ServiceForm(
        form_number=form_number,
        technician_id=current_user.id,
        status="OPEN",
        started_at=datetime.utcnow(),
        **form_data.model_dump()
    )
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    
    return {
        **db_form.__dict__,
        "items": [],
        "project_code": project.project_code,
        "technician_name": current_user.full_name
    }


@router.get("/{form_id}", response_model=ServiceFormResponse)
async def get_service_form(form_id: int, db: Session = Depends(get_db)):
    """Get service form details with used materials"""
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    project = db.query(Project).filter(Project.id == form.project_id).first()
    technician = db.query(User).filter(User.id == form.technician_id).first()
    items = db.query(ServiceFormItem).filter(ServiceFormItem.service_form_id == form.id).all()
    
    items_response = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_response.append({
            "id": item.id,
            "service_form_id": item.service_form_id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": item.quantity,
            "delivered_to_customer": item.delivered_to_customer,
            "notes": item.notes
        })
    
    return {
        **form.__dict__,
        "items": items_response,
        "project_code": project.project_code if project else None,
        "technician_name": technician.full_name if technician else None
    }


@router.put("/{form_id}", response_model=ServiceFormResponse)
async def update_service_form(
    form_id: int,
    form_update: ServiceFormUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update service form (add materials, notes, etc.)"""
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    if form.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Tamamlanmış form güncellenemez")
    
    update_data = form_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(form, key, value)
    
    # If updating, set status to IN_PROGRESS
    if form.status == "OPEN":
        form.status = "IN_PROGRESS"
    
    db.commit()
    db.refresh(form)
    
    project = db.query(Project).filter(Project.id == form.project_id).first()
    technician = db.query(User).filter(User.id == form.technician_id).first()
    items = db.query(ServiceFormItem).filter(ServiceFormItem.service_form_id == form.id).all()
    
    items_response = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_response.append({
            "id": item.id,
            "service_form_id": item.service_form_id,
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "product_sku": product.sku if product else None,
            "quantity": item.quantity,
            "delivered_to_customer": item.delivered_to_customer,
            "notes": item.notes
        })
    
    return {
        **form.__dict__,
        "items": items_response,
        "project_code": project.project_code if project else None,
        "technician_name": technician.full_name if technician else None
    }


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete service form (only if OPEN status)"""
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    if form.status != "OPEN":
        raise HTTPException(status_code=400, detail="Sadece açık formlar silinebilir")
    
    # Delete items first
    db.query(ServiceFormItem).filter(ServiceFormItem.service_form_id == form_id).delete()
    db.delete(form)
    db.commit()


@router.post("/{form_id}/add-material", response_model=ServiceFormItemResponse)
async def add_material_to_form(
    form_id: int,
    item: ServiceFormItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add used material to service form.
    Does not deduct from stock yet - only records usage.
    """
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    if form.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Tamamlanmış forma malzeme eklenemez")
    
    # Validate product
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    db_item = ServiceFormItem(
        service_form_id=form_id,
        **item.model_dump()
    )
    db.add(db_item)
    
    # Update form status
    if form.status == "OPEN":
        form.status = "IN_PROGRESS"
    
    db.commit()
    db.refresh(db_item)
    
    return {
        "id": db_item.id,
        "service_form_id": db_item.service_form_id,
        "product_id": db_item.product_id,
        "product_name": product.name,
        "product_sku": product.sku,
        "quantity": db_item.quantity,
        "delivered_to_customer": db_item.delivered_to_customer,
        "notes": db_item.notes
    }


@router.delete("/{form_id}/materials/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_material_from_form(
    form_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove material from service form"""
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    if form.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Tamamlanmış formdan malzeme çıkarılamaz")
    
    item = db.query(ServiceFormItem).filter(
        ServiceFormItem.id == item_id,
        ServiceFormItem.service_form_id == form_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Malzeme bulunamadı")
    
    db.delete(item)
    db.commit()


@router.post("/{form_id}/complete")
async def complete_service_form(
    form_id: int,
    complete_data: ServiceFormComplete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Complete service form and finalize stock movements.
    
    Business Rules:
    - Deducts all materials from vehicle warehouse
    - Materials marked as 'delivered_to_customer' leave inventory
    - Cannot complete if vehicle warehouse has insufficient stock
    """
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    if form.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Form zaten tamamlanmış")
    
    items = db.query(ServiceFormItem).filter(ServiceFormItem.service_form_id == form_id).all()
    
    # Check stock availability in vehicle warehouse
    if form.vehicle_warehouse_id:
        for item in items:
            stock = db.query(WarehouseStock).filter(
                WarehouseStock.warehouse_id == form.vehicle_warehouse_id,
                WarehouseStock.product_id == item.product_id
            ).first()
            
            available = stock.quantity if stock else Decimal("0")
            if available < item.quantity:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                raise HTTPException(
                    status_code=400,
                    detail=f"Yetersiz stok: {product.name if product else 'Bilinmeyen'}. Mevcut: {available}, Gerekli: {item.quantity}"
                )
    
    # Deduct stock and create movements
    for item in items:
        if form.vehicle_warehouse_id:
            stock = db.query(WarehouseStock).filter(
                WarehouseStock.warehouse_id == form.vehicle_warehouse_id,
                WarehouseStock.product_id == item.product_id
            ).first()
            
            if stock:
                stock.quantity -= item.quantity
        
        # Create movement record
        product = db.query(Product).filter(Product.id == item.product_id).first()
        movement = StockMovement(
            project_id=form.project_id,
            product_id=item.product_id,
            movement_type=MovementType.SERVICE.value,
            from_warehouse_id=form.vehicle_warehouse_id,
            quantity=item.quantity,
            unit_cost=product.cost if product else None,
            reference_type="service_form",
            reference_id=form.id,
            notes=f"Servis formu: {form.form_number}",
            created_by=current_user.id
        )
        db.add(movement)
    
    # Update form
    form.status = "COMPLETED"
    form.work_performed = complete_data.work_performed
    form.customer_name = complete_data.customer_name
    form.customer_signed = complete_data.customer_signed
    form.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Servis formu tamamlandı",
        "form_number": form.form_number,
        "items_processed": len(items)
    }


@router.get("/{form_id}/pdf")
async def get_service_form_pdf(form_id: int, db: Session = Depends(get_db)):
    """Get PDF for service form"""
    form = db.query(ServiceForm).filter(ServiceForm.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Servis formu bulunamadı")
    
    # TODO: Implement PDF generation with ReportLab
    return {
        "form_id": form_id,
        "form_number": form.form_number,
        "pdf_url": f"/uploads/service-forms/{form_id}.pdf"
    }
