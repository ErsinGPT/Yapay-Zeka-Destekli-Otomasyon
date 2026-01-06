"""
Invoices Router
Handles domestic and export invoice management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.models import Invoice, InvoiceItem, Project, Customer, Product
from app.schemas import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    InvoiceItemCreate, InvoiceItemResponse
)
from app.routers.auth import get_current_user

router = APIRouter()

# Invoice types and statuses
INVOICE_TYPES = ["DOMESTIC", "EXPORT"]
INVOICE_STATUSES = ["DRAFT", "SENT", "PAID", "CANCELLED"]


def generate_invoice_number(db: Session, invoice_type: str = "DOMESTIC") -> str:
    """Generate unique invoice number"""
    year = datetime.now().year
    prefix = "FTR" if invoice_type == "DOMESTIC" else "EXP"
    
    last_invoice = db.query(Invoice).filter(
        Invoice.invoice_number.like(f"{prefix}-{year}-%")
    ).order_by(Invoice.id.desc()).first()
    
    if last_invoice:
        last_num = int(last_invoice.invoice_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{year}-{new_num:06d}"


def calculate_invoice_totals(items: List[InvoiceItemCreate], vat_rate: Decimal) -> dict:
    """Calculate invoice subtotal, tax, and total"""
    subtotal = Decimal("0")
    total_discount = Decimal("0")
    
    for item in items:
        line_subtotal = item.quantity * item.unit_price
        subtotal += line_subtotal
        total_discount += item.discount
    
    taxable = subtotal - total_discount
    tax_amount = taxable * (vat_rate / Decimal("100"))
    total = taxable + tax_amount
    
    return {
        "subtotal": subtotal,
        "discount": total_discount,
        "tax_amount": tax_amount,
        "total": total
    }


@router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    project_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    invoice_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get all invoices with filtering options"""
    query = db.query(Invoice)
    
    if project_id:
        query = query.filter(Invoice.project_id == project_id)
    
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if search:
        query = query.filter(Invoice.invoice_number.ilike(f"%{search}%"))
    
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for inv in invoices:
        customer = db.query(Customer).filter(Customer.id == inv.customer_id).first()
        project = db.query(Project).filter(Project.id == inv.project_id).first()
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv.id).all()
        
        items_response = []
        for item in items:
            items_response.append({
                "id": item.id,
                "invoice_id": item.invoice_id,
                "product_id": item.product_id,
                "description": item.description,
                "description_en": item.description_en,
                "gtip_code": item.gtip_code,
                "quantity": item.quantity,
                "unit": item.unit,
                "unit_price": item.unit_price,
                "discount": item.discount,
                "vat_rate": item.vat_rate,
                "vat_amount": item.vat_amount,
                "total": item.total
            })
        
        result.append({
            **inv.__dict__,
            "items": items_response,
            "customer_name": customer.name if customer else None,
            "project_code": project.project_code if project else None
        })
    
    return result


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create new invoice.
    For EXPORT type, GTIP codes and English descriptions are required.
    """
    # Validate project
    project = db.query(Project).filter(Project.id == invoice_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate customer
    customer = db.query(Customer).filter(Customer.id == invoice_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")
    
    # Validate invoice type
    if invoice_data.invoice_type not in INVOICE_TYPES:
        raise HTTPException(status_code=400, detail=f"Geçersiz fatura tipi. İzin verilen: {INVOICE_TYPES}")
    
    # For export invoices, validate GTIP and English descriptions
    if invoice_data.invoice_type == "EXPORT":
        for item in invoice_data.items:
            if not item.gtip_code:
                raise HTTPException(status_code=400, detail="İhracat faturası için GTIP kodu zorunludur")
            if not item.description_en:
                raise HTTPException(status_code=400, detail="İhracat faturası için İngilizce açıklama zorunludur")
    
    # Calculate totals
    vat_rate = Decimal("0") if invoice_data.invoice_type == "EXPORT" else invoice_data.vat_rate
    totals = calculate_invoice_totals(invoice_data.items, vat_rate)
    
    invoice_number = generate_invoice_number(db, invoice_data.invoice_type)
    
    # Create invoice
    db_invoice = Invoice(
        invoice_number=invoice_number,
        project_id=invoice_data.project_id,
        customer_id=invoice_data.customer_id,
        invoice_type=invoice_data.invoice_type,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        currency=invoice_data.currency,
        exchange_rate=invoice_data.exchange_rate,
        vat_rate=vat_rate,
        subtotal=totals["subtotal"],
        discount=totals["discount"],
        tax_amount=totals["tax_amount"],
        total=totals["total"],
        status="DRAFT",
        notes=invoice_data.notes,
        created_by=current_user.id
    )
    db.add(db_invoice)
    db.flush()
    
    # Create items
    for item_data in invoice_data.items:
        line_subtotal = item_data.quantity * item_data.unit_price - item_data.discount
        item_vat = line_subtotal * (vat_rate / Decimal("100"))
        line_total = line_subtotal + item_vat
        
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            product_id=item_data.product_id,
            description=item_data.description,
            description_en=item_data.description_en,
            gtip_code=item_data.gtip_code,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            discount=item_data.discount,
            vat_rate=vat_rate,
            vat_amount=item_vat,
            total=line_total
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_invoice)
    
    # Build response
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == db_invoice.id).all()
    items_response = [
        {
            "id": item.id,
            "invoice_id": item.invoice_id,
            "product_id": item.product_id,
            "description": item.description,
            "description_en": item.description_en,
            "gtip_code": item.gtip_code,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "vat_rate": item.vat_rate,
            "vat_amount": item.vat_amount,
            "total": item.total
        }
        for item in items
    ]
    
    return {
        **db_invoice.__dict__,
        "items": items_response,
        "customer_name": customer.name,
        "project_code": project.project_code
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Get invoice details"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    project = db.query(Project).filter(Project.id == invoice.project_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    
    items_response = [
        {
            "id": item.id,
            "invoice_id": item.invoice_id,
            "product_id": item.product_id,
            "description": item.description,
            "description_en": item.description_en,
            "gtip_code": item.gtip_code,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "vat_rate": item.vat_rate,
            "vat_amount": item.vat_amount,
            "total": item.total
        }
        for item in items
    ]
    
    return {
        **invoice.__dict__,
        "items": items_response,
        "customer_name": customer.name if customer else None,
        "project_code": project.project_code if project else None
    }


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update invoice.
    Cannot update if status is PAID or CANCELLED.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    if invoice.status in ["PAID", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Ödenmiş veya iptal edilmiş fatura güncellenemez")
    
    update_data = invoice_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)
    
    db.commit()
    db.refresh(invoice)
    
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    project = db.query(Project).filter(Project.id == invoice.project_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    
    items_response = [
        {
            "id": item.id,
            "invoice_id": item.invoice_id,
            "product_id": item.product_id,
            "description": item.description,
            "description_en": item.description_en,
            "gtip_code": item.gtip_code,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "vat_rate": item.vat_rate,
            "vat_amount": item.vat_amount,
            "total": item.total
        }
        for item in items
    ]
    
    return {
        **invoice.__dict__,
        "items": items_response,
        "customer_name": customer.name if customer else None,
        "project_code": project.project_code if project else None
    }


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete invoice (only DRAFT status)"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    if invoice.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Sadece taslak faturalar silinebilir")
    
    # Delete items first
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
    db.delete(invoice)
    db.commit()


@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send invoice via e-Fatura API.
    This is a pluggable interface - actual implementation depends on integrator.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    if invoice.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Sadece taslak faturalar gönderilebilir")
    
    # TODO: Implement actual e-Fatura integration
    # For now, just update status
    invoice.status = "SENT"
    invoice.e_invoice_status = "PENDING"
    
    db.commit()
    
    return {
        "message": "Fatura gönderildi",
        "invoice_number": invoice.invoice_number,
        "status": "SENT",
        "e_invoice_status": "PENDING"
    }


@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark invoice as paid"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    if invoice.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="İptal edilmiş fatura ödenmiş olarak işaretlenemez")
    
    invoice.status = "PAID"
    db.commit()
    
    return {
        "message": "Fatura ödendi olarak işaretlendi",
        "invoice_number": invoice.invoice_number
    }


@router.post("/{invoice_id}/cancel")
async def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel invoice"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    if invoice.status == "PAID":
        raise HTTPException(status_code=400, detail="Ödenmiş fatura iptal edilemez")
    
    invoice.status = "CANCELLED"
    db.commit()
    
    return {
        "message": "Fatura iptal edildi",
        "invoice_number": invoice.invoice_number
    }


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    """Generate and download invoice PDF"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    
    # TODO: Implement PDF generation with ReportLab
    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice.invoice_number,
        "pdf_url": f"/uploads/invoices/{invoice_id}.pdf"
    }
