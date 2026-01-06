"""
Customers Router
Full CRUD for customer management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.utils.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all customers with optional filtering.
    
    - **search**: Search by name, email, or contact person
    - **is_active**: Filter by active status
    """
    query = db.query(Customer)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_term)) |
            (Customer.email.ilike(search_term)) |
            (Customer.contact_person.ilike(search_term))
        )
    
    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)
    
    customers = query.order_by(Customer.name).offset(skip).limit(limit).all()
    return customers


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new customer."""
    # Check for duplicate tax_id if provided
    if customer_data.tax_id:
        existing = db.query(Customer).filter(Customer.tax_id == customer_data.tax_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu vergi numarası ile kayıtlı müşteri zaten mevcut"
            )
    
    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a single customer by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müşteri bulunamadı"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müşteri bulunamadı"
        )
    
    # Check for duplicate tax_id if updating
    if customer_data.tax_id and customer_data.tax_id != customer.tax_id:
        existing = db.query(Customer).filter(
            Customer.tax_id == customer_data.tax_id,
            Customer.id != customer_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu vergi numarası ile kayıtlı başka müşteri mevcut"
            )
    
    # Update only provided fields
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Delete a customer permanently.
    Only admins can delete customers.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müşteri bulunamadı"
        )
    
    # Check if customer has related records (opportunities, projects, etc.)
    from app.models import Opportunity, Project
    
    has_opportunities = db.query(Opportunity).filter(Opportunity.customer_id == customer_id).first()
    has_projects = db.query(Project).filter(Project.customer_id == customer_id).first()
    
    if has_opportunities or has_projects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu müşteriye ait fırsat veya proje bulunmaktadır. Önce ilişkili kayıtları silin."
        )
    
    # Hard delete
    db.delete(customer)
    db.commit()
    
    return {"message": "Müşteri silindi"}
