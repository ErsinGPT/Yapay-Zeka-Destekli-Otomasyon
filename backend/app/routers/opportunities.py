"""
Opportunities Router
Handles sales opportunities/leads management with quotes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Opportunity, Customer, Quote, Project
from app.models.project import OpportunityStatus
from app.schemas import (
    OpportunityCreate, OpportunityUpdate, OpportunityResponse,
    QuoteCreate, QuoteResponse, ProjectResponse
)
from app.utils.auth import get_current_user

router = APIRouter()


def generate_project_code(db: Session) -> str:
    """
    Generate unique project code in format PRJ-YYYY-XXXX
    Example: PRJ-2026-0001
    """
    current_year = datetime.now().year
    
    # Find the last project code for this year
    last_project = db.query(Project).filter(
        Project.project_code.like(f"PRJ-{current_year}-%")
    ).order_by(Project.project_code.desc()).first()
    
    if last_project:
        # Extract the sequence number and increment
        try:
            last_seq = int(last_project.project_code.split("-")[-1])
            new_seq = last_seq + 1
        except ValueError:
            new_seq = 1
    else:
        new_seq = 1
    
    return f"PRJ-{current_year}-{new_seq:04d}"


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all opportunities with optional filtering.
    
    - **status**: Filter by status (NEW, CONTACTED, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST)
    - **customer_id**: Filter by customer
    """
    query = db.query(Opportunity)
    
    if status:
        query = query.filter(Opportunity.status == status)
    
    if customer_id:
        query = query.filter(Opportunity.customer_id == customer_id)
    
    opportunities = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add customer name to response
    result = []
    for opp in opportunities:
        opp_dict = {
            "id": opp.id,
            "title": opp.title,
            "description": opp.description,
            "customer_id": opp.customer_id,
            "expected_revenue": opp.expected_revenue,
            "currency": opp.currency,
            "status": opp.status,
            "probability": opp.probability,
            "expected_close_date": opp.expected_close_date,
            "closed_date": opp.closed_date,
            "assigned_to": opp.assigned_to,
            "created_at": opp.created_at,
            "updated_at": opp.updated_at,
            "customer_name": opp.customer.name if opp.customer else None
        }
        result.append(OpportunityResponse(**opp_dict))
    
    return result


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new opportunity."""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == opportunity_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müşteri bulunamadı"
        )
    
    opportunity = Opportunity(**opportunity_data.model_dump())
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    return OpportunityResponse(
        **{k: v for k, v in opportunity.__dict__.items() if not k.startswith('_')},
        customer_name=customer.name
    )


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a single opportunity by ID."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    return OpportunityResponse(
        **{k: v for k, v in opportunity.__dict__.items() if not k.startswith('_')},
        customer_name=opportunity.customer.name if opportunity.customer else None
    )


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    # Validate status if provided
    if opportunity_data.status:
        valid_statuses = [s.value for s in OpportunityStatus]
        if opportunity_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz durum. Geçerli durumlar: {valid_statuses}"
            )
    
    # Update only provided fields
    update_data = opportunity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    db.commit()
    db.refresh(opportunity)
    
    return OpportunityResponse(
        **{k: v for k, v in opportunity.__dict__.items() if not k.startswith('_')},
        customer_name=opportunity.customer.name if opportunity.customer else None
    )


@router.post("/{opportunity_id}/won", response_model=ProjectResponse)
async def mark_opportunity_won(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark opportunity as won and create a project.
    
    - Generates automatic ProjectID in format PRJ-YYYY-XXXX
    - Creates a new project linked to this opportunity
    - Updates opportunity status to WON
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    # Check if already won
    if opportunity.status == OpportunityStatus.WON.value:
        # Return existing project
        existing_project = db.query(Project).filter(Project.opportunity_id == opportunity_id).first()
        if existing_project:
            return ProjectResponse(
                **{k: v for k, v in existing_project.__dict__.items() if not k.startswith('_')},
                customer_name=opportunity.customer.name if opportunity.customer else None
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu fırsat zaten kazanıldı"
        )
    
    # Generate project code
    project_code = generate_project_code(db)
    
    # Create project
    project = Project(
        project_code=project_code,
        title=opportunity.title,
        description=opportunity.description,
        customer_id=opportunity.customer_id,
        opportunity_id=opportunity.id,
        contract_amount=opportunity.expected_revenue,
        currency=opportunity.currency,
        status="WON",
        start_date=datetime.utcnow()
    )
    
    # Update opportunity
    opportunity.status = OpportunityStatus.WON.value
    opportunity.closed_date = datetime.utcnow()
    opportunity.probability = 100
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        **{k: v for k, v in project.__dict__.items() if not k.startswith('_')},
        customer_name=opportunity.customer.name if opportunity.customer else None
    )


@router.post("/{opportunity_id}/lost")
async def mark_opportunity_lost(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark opportunity as lost."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    opportunity.status = OpportunityStatus.LOST.value
    opportunity.closed_date = datetime.utcnow()
    opportunity.probability = 0
    
    db.commit()
    
    return {"message": "Fırsat kaybedildi olarak işaretlendi"}


@router.get("/{opportunity_id}/quotes", response_model=List[QuoteResponse])
async def get_quotes(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all quotes for an opportunity."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    quotes = db.query(Quote).filter(Quote.opportunity_id == opportunity_id).order_by(Quote.version.desc()).all()
    return quotes


@router.post("/{opportunity_id}/quotes", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    opportunity_id: int,
    quote_data: QuoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new quote for an opportunity.
    
    Supports multi-currency quotes (TRY, USD, EUR).
    Auto-increments version number.
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    # Get next version number
    max_version = db.query(func.max(Quote.version)).filter(Quote.opportunity_id == opportunity_id).scalar()
    next_version = (max_version or 0) + 1
    
    quote = Quote(
        opportunity_id=opportunity_id,
        version=next_version,
        **quote_data.model_dump()
    )
    
    db.add(quote)
    db.commit()
    db.refresh(quote)
    
    return quote


@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an opportunity.
    
    - If the opportunity was WON, the related project and all its data will be deleted
    - All related quotes will be deleted
    """
    from sqlalchemy import text
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fırsat bulunamadı"
        )
    
    try:
        # Disable foreign key checks temporarily for SQLite
        db.execute(text("PRAGMA foreign_keys = OFF"))
        
        # If WON, delete related project and all its dependencies
        if opportunity.status == OpportunityStatus.WON.value:
            project = db.query(Project).filter(Project.opportunity_id == opportunity_id).first()
            if project:
                project_id = project.id
                
                # Delete in correct order using parameterized queries
                db.execute(text("DELETE FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE project_id = :pid)"), {"pid": project_id})
                db.execute(text("DELETE FROM service_form_items WHERE service_form_id IN (SELECT id FROM service_forms WHERE project_id = :pid)"), {"pid": project_id})
                db.execute(text("DELETE FROM delivery_note_items WHERE delivery_note_id IN (SELECT id FROM delivery_notes WHERE project_id = :pid)"), {"pid": project_id})
                db.execute(text("DELETE FROM stock_movements WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM stock_reservations WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM delivery_notes WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM service_forms WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM invoices WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM expenses WHERE project_id = :pid"), {"pid": project_id})
                db.execute(text("DELETE FROM projects WHERE id = :pid"), {"pid": project_id})
        
        # Delete related quotes
        db.execute(text("DELETE FROM quotes WHERE opportunity_id = :oid"), {"oid": opportunity_id})
        
        # Delete opportunity
        db.execute(text("DELETE FROM opportunities WHERE id = :oid"), {"oid": opportunity_id})
        
        db.commit()
        
        # Re-enable foreign key checks
        db.execute(text("PRAGMA foreign_keys = ON"))
        
        return {"message": "Fırsat silindi"}
        
    except Exception as e:
        db.rollback()
        db.execute(text("PRAGMA foreign_keys = ON"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Silme işlemi başarısız: {str(e)}"
        )
