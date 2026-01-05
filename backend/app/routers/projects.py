"""
Projects Router
Handles project management with Waterfall lifecycle
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models import Project, Customer, Invoice, Expense, StockMovement
from app.models.project import ProjectStatus
from app.schemas import (
    ProjectResponse, ProjectUpdate, ProjectStatusUpdate, ProjectSummary
)
from app.utils.auth import get_current_user, require_manager

router = APIRouter()

# Waterfall project statuses - ordered
PROJECT_STATUSES = [
    ProjectStatus.OPPORTUNITY.value,
    ProjectStatus.WON.value,
    ProjectStatus.ENGINEERING.value,
    ProjectStatus.PROCUREMENT.value,
    ProjectStatus.ASSEMBLY.value,
    ProjectStatus.TESTING.value,
    ProjectStatus.SHIPPING.value,
    ProjectStatus.COMMISSIONING.value,
    ProjectStatus.COMPLETED.value,
    ProjectStatus.INVOICED.value
]


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all projects with optional filtering.
    
    - **status**: Filter by Waterfall status
    - **customer_id**: Filter by customer
    - **search**: Search by project code or title
    """
    query = db.query(Project)
    
    if status:
        query = query.filter(Project.status == status)
    
    if customer_id:
        query = query.filter(Project.customer_id == customer_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Project.project_code.ilike(search_term)) |
            (Project.title.ilike(search_term))
        )
    
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add customer name
    result = []
    for proj in projects:
        result.append(ProjectResponse(
            **{k: v for k, v in proj.__dict__.items() if not k.startswith('_')},
            customer_name=proj.customer.name if proj.customer else None
        ))
    
    return result


@router.get("/statuses")
async def get_project_statuses():
    """Get all available project statuses (Waterfall lifecycle)."""
    return {
        "statuses": PROJECT_STATUSES,
        "descriptions": {
            "OPPORTUNITY": "Fırsat aşamasında",
            "WON": "Kazanıldı - Proje başladı",
            "ENGINEERING": "Mühendislik tasarım aşaması",
            "PROCUREMENT": "Tedarik/Satın alma aşaması",
            "ASSEMBLY": "Montaj aşaması",
            "TESTING": "Test aşaması",
            "SHIPPING": "Sevkiyat aşaması",
            "COMMISSIONING": "Devreye alma aşaması",
            "COMPLETED": "Tamamlandı",
            "INVOICED": "Faturalandı"
        }
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a single project with details."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı"
        )
    
    return ProjectResponse(
        **{k: v for k, v in project.__dict__.items() if not k.startswith('_')},
        customer_name=project.customer.name if project.customer else None
    )


@router.get("/code/{project_code}", response_model=ProjectResponse)
async def get_project_by_code(
    project_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a project by its unique code (e.g., PRJ-2026-0001)."""
    project = db.query(Project).filter(Project.project_code == project_code).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı"
        )
    
    return ProjectResponse(
        **{k: v for k, v in project.__dict__.items() if not k.startswith('_')},
        customer_name=project.customer.name if project.customer else None
    )


@router.get("/{project_id}/summary", response_model=ProjectSummary)
async def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get project profitability summary.
    
    Returns: Revenue, Material Cost, Labor Cost, Expenses, Net Profit, Profit Margin
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı"
        )
    
    # Calculate revenue from invoices
    revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.project_id == project_id
    ).scalar() or Decimal("0")
    
    # Calculate expenses
    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.project_id == project_id
    ).scalar() or Decimal("0")
    
    # Calculate material cost from stock movements
    # This is simplified - in reality you'd calculate cost from materials used
    material_cost = Decimal("0")
    stock_movements = db.query(StockMovement).filter(
        StockMovement.project_id == project_id,
        StockMovement.movement_type == "RESERVE"
    ).all()
    
    for movement in stock_movements:
        if movement.unit_cost:
            material_cost += movement.quantity * movement.unit_cost
    
    # Labor cost would come from time tracking (not implemented)
    labor_cost = Decimal("0")
    
    # Calculate net profit
    total_cost = material_cost + labor_cost + expenses
    net_profit = revenue - total_cost
    
    # Calculate profit margin
    if revenue > 0:
        profit_margin = float((net_profit / revenue) * 100)
    else:
        profit_margin = 0.0
    
    return ProjectSummary(
        project_id=project_id,
        project_code=project.project_code,
        revenue=revenue,
        material_cost=material_cost,
        labor_cost=labor_cost,
        expenses=expenses,
        net_profit=net_profit,
        profit_margin=round(profit_margin, 2)
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update project details."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı"
        )
    
    # Update only provided fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        **{k: v for k, v in project.__dict__.items() if not k.startswith('_')},
        customer_name=project.customer.name if project.customer else None
    )


@router.put("/{project_id}/status", response_model=ProjectResponse)
async def update_project_status(
    project_id: int,
    status_update: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_manager)
):
    """
    Update project status (Waterfall progression).
    
    Only managers and admins can change status.
    Validates that the new status is valid.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı"
        )
    
    new_status = status_update.status
    
    # Validate status
    if new_status not in PROJECT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz durum. Geçerli durumlar: {PROJECT_STATUSES}"
        )
    
    # Optional: Validate status progression (can only move forward or back one step)
    # current_index = PROJECT_STATUSES.index(project.status)
    # new_index = PROJECT_STATUSES.index(new_status)
    # if abs(new_index - current_index) > 1:
    #     raise HTTPException(...)
    
    project.status = new_status
    db.commit()
    db.refresh(project)
    
    return ProjectResponse(
        **{k: v for k, v in project.__dict__.items() if not k.startswith('_')},
        customer_name=project.customer.name if project.customer else None
    )
