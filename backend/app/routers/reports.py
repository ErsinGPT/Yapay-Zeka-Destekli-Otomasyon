"""
Reports Router
Handles reporting and analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import get_db
from app.models import (
    Project, Invoice, Expense, WarehouseStock, Product, StockMovement,
    Customer, Opportunity, StockReservation, ProjectStatus
)
from app.schemas import (
    DashboardStats, StockStatusReport, ExpenseSummaryReport,
    RevenueSummaryReport, CurrencyRates
)
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard statistics"""
    # Total projects
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    
    # Active projects (not COMPLETED, INVOICED, CLOSED)
    inactive_statuses = ["COMPLETED", "INVOICED", "CLOSED", "CANCELLED"]
    active_projects = db.query(func.count(Project.id)).filter(
        ~Project.status.in_(inactive_statuses)
    ).scalar() or 0
    
    # Total revenue (from paid invoices)
    total_revenue = db.query(func.sum(Invoice.total)).filter(
        Invoice.status == "PAID"
    ).scalar() or Decimal("0")
    
    # Total expenses (approved)
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.status == "APPROVED"
    ).scalar() or Decimal("0")
    
    # Pending invoices
    pending_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.status.in_(["DRAFT", "SENT"])
    ).scalar() or 0
    
    # Low stock items
    low_stock_items = 0
    products_with_min = db.query(Product).filter(
        Product.min_stock_level > 0,
        Product.is_active == True
    ).all()
    
    for product in products_with_min:
        total_stock = db.query(func.sum(WarehouseStock.quantity)).filter(
            WarehouseStock.product_id == product.id
        ).scalar() or Decimal("0")
        
        if total_stock < product.min_stock_level:
            low_stock_items += 1
    
    return DashboardStats(
        total_projects=total_projects,
        active_projects=active_projects,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        pending_invoices=pending_invoices,
        low_stock_items=low_stock_items
    )


@router.get("/project-profitability/{project_id}")
async def get_project_profitability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed project profitability report.
    
    Formula: Profit = Revenue - (Material Cost + Labor + Expenses)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Revenue from invoices
    revenue = db.query(func.sum(Invoice.total)).filter(
        Invoice.project_id == project_id,
        Invoice.status.in_(["SENT", "PAID"])
    ).scalar() or Decimal("0")
    
    # Material cost from stock movements
    material_cost = db.query(func.sum(StockMovement.quantity * StockMovement.unit_cost)).filter(
        StockMovement.project_id == project_id,
        StockMovement.movement_type.in_(["OUT", "SERVICE", "CONSUMPTION"])
    ).scalar() or Decimal("0")
    
    # Labor cost (TODO: implement timesheet tracking)
    labor_cost = Decimal("0")
    
    # Expenses
    expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.project_id == project_id,
        Expense.status == "APPROVED"
    ).scalar() or Decimal("0")
    
    total_cost = material_cost + labor_cost + expenses
    profit = revenue - total_cost
    margin_percent = (float(profit) / float(revenue) * 100) if revenue > 0 else 0
    
    return {
        "project_id": project_id,
        "project_code": project.project_code,
        "project_title": project.title,
        "revenue": {
            "invoices": float(revenue),
            "currency": project.currency
        },
        "costs": {
            "materials": float(material_cost),
            "labor": float(labor_cost),
            "expenses": float(expenses),
            "total": float(total_cost)
        },
        "profit": float(profit),
        "margin_percent": round(margin_percent, 2)
    }


@router.get("/stock-status", response_model=StockStatusReport)
async def get_stock_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive stock status report.
    Shows physical vs available stock across all warehouses.
    """
    from app.models import Warehouse
    
    # Warehouses with stock summary
    warehouses_data = []
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    
    for wh in warehouses:
        stock_summary = db.query(
            func.sum(WarehouseStock.quantity).label("total"),
            func.sum(WarehouseStock.reserved_quantity).label("reserved"),
            func.count(WarehouseStock.id).label("item_count")
        ).filter(WarehouseStock.warehouse_id == wh.id).first()
        
        warehouses_data.append({
            "id": wh.id,
            "name": wh.name,
            "code": wh.code,
            "type": wh.warehouse_type,
            "total_quantity": float(stock_summary.total or 0),
            "reserved_quantity": float(stock_summary.reserved or 0),
            "available_quantity": float((stock_summary.total or 0) - (stock_summary.reserved or 0)),
            "item_count": stock_summary.item_count or 0
        })
    
    # Low stock alerts
    low_stock_alerts = []
    products_with_min = db.query(Product).filter(
        Product.min_stock_level > 0,
        Product.is_active == True
    ).all()
    
    for product in products_with_min:
        total_stock = db.query(func.sum(WarehouseStock.quantity)).filter(
            WarehouseStock.product_id == product.id
        ).scalar() or Decimal("0")
        
        if total_stock < product.min_stock_level:
            low_stock_alerts.append({
                "product_id": product.id,
                "sku": product.sku,
                "name": product.name,
                "current_stock": float(total_stock),
                "min_level": product.min_stock_level,
                "shortage": product.min_stock_level - float(total_stock)
            })
    
    # Reserved items
    reserved_items = []
    reservations = db.query(StockReservation).filter(
        StockReservation.status == "ACTIVE"
    ).all()
    
    for res in reservations:
        product = db.query(Product).filter(Product.id == res.product_id).first()
        project = db.query(Project).filter(Project.id == res.project_id).first()
        
        reserved_items.append({
            "reservation_id": res.id,
            "product_name": product.name if product else None,
            "project_code": project.project_code if project else None,
            "quantity": float(res.quantity),
            "created_at": res.created_at.isoformat() if res.created_at else None
        })
    
    return StockStatusReport(
        warehouses=warehouses_data,
        low_stock_alerts=low_stock_alerts,
        reserved_items=reserved_items
    )


@router.get("/expense-summary", response_model=ExpenseSummaryReport)
async def get_expense_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get expense summary by project, type, and personnel.
    """
    from app.models import User
    
    query = db.query(Expense).filter(Expense.status == "APPROVED")
    
    if start_date:
        query = query.filter(Expense.created_at >= start_date)
    if end_date:
        query = query.filter(Expense.created_at <= end_date)
    
    expenses = query.all()
    
    total = sum(exp.amount for exp in expenses)
    
    # By project
    project_totals = {}
    for exp in expenses:
        project = db.query(Project).filter(Project.id == exp.project_id).first()
        key = project.project_code if project else "Bilinmeyen"
        project_totals[key] = project_totals.get(key, Decimal("0")) + exp.amount
    
    by_project = [{"project": k, "amount": float(v)} for k, v in project_totals.items()]
    
    # By type
    type_totals = {}
    for exp in expenses:
        type_totals[exp.expense_type] = type_totals.get(exp.expense_type, Decimal("0")) + exp.amount
    
    by_type = [{"type": k, "amount": float(v)} for k, v in type_totals.items()]
    
    # By personnel
    personnel_totals = {}
    for exp in expenses:
        user = db.query(User).filter(User.id == exp.user_id).first()
        key = user.full_name if user else "Bilinmeyen"
        personnel_totals[key] = personnel_totals.get(key, Decimal("0")) + exp.amount
    
    by_personnel = [{"name": k, "amount": float(v)} for k, v in personnel_totals.items()]
    
    return ExpenseSummaryReport(
        total=total,
        by_project=sorted(by_project, key=lambda x: x["amount"], reverse=True),
        by_type=sorted(by_type, key=lambda x: x["amount"], reverse=True),
        by_personnel=sorted(by_personnel, key=lambda x: x["amount"], reverse=True)
    )


@router.get("/revenue-summary", response_model=RevenueSummaryReport)
async def get_revenue_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get revenue summary by project and period.
    """
    query = db.query(Invoice).filter(Invoice.status.in_(["SENT", "PAID"]))
    
    if start_date:
        query = query.filter(Invoice.invoice_date >= start_date)
    if end_date:
        query = query.filter(Invoice.invoice_date <= end_date)
    
    invoices = query.all()
    
    total = sum(inv.total for inv in invoices)
    
    # By project
    project_totals = {}
    for inv in invoices:
        project = db.query(Project).filter(Project.id == inv.project_id).first()
        key = project.project_code if project else "Bilinmeyen"
        project_totals[key] = project_totals.get(key, Decimal("0")) + inv.total
    
    by_project = [{"project": k, "amount": float(v)} for k, v in project_totals.items()]
    
    # By month
    month_totals = {}
    for inv in invoices:
        if inv.invoice_date:
            key = inv.invoice_date.strftime("%Y-%m")
            month_totals[key] = month_totals.get(key, Decimal("0")) + inv.total
    
    by_month = [{"month": k, "amount": float(v)} for k, v in sorted(month_totals.items())]
    
    return RevenueSummaryReport(
        total=total,
        by_project=sorted(by_project, key=lambda x: x["amount"], reverse=True),
        by_month=by_month
    )


@router.get("/currency-rates", response_model=CurrencyRates)
async def get_currency_rates(db: Session = Depends(get_db)):
    """
    Get current currency rates from TCMB.
    Rates are automatically updated twice daily.
    """
    from app.models import CurrencyRate
    
    rates = db.query(CurrencyRate).all()
    
    rates_dict = {}
    last_updated = datetime.now()
    
    for rate in rates:
        rates_dict[rate.currency_code] = {
            "buying": float(rate.buying_rate),
            "selling": float(rate.selling_rate)
        }
        if rate.updated_at and rate.updated_at < last_updated:
            last_updated = rate.updated_at
    
    # If no rates in DB, return placeholder
    if not rates_dict:
        rates_dict = {
            "USD": {"buying": 35.50, "selling": 35.60},
            "EUR": {"buying": 38.20, "selling": 38.35}
        }
        last_updated = datetime.now()
    
    return CurrencyRates(
        last_updated=last_updated,
        rates=rates_dict
    )


@router.get("/opportunities-pipeline")
async def get_opportunities_pipeline(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get opportunities pipeline summary"""
    from app.models import OpportunityStatus
    
    pipeline = []
    
    for status in ["NEW", "QUALIFICATION", "PROPOSAL", "NEGOTIATION"]:
        count = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == status
        ).scalar() or 0
        
        total_value = db.query(func.sum(Opportunity.expected_revenue)).filter(
            Opportunity.status == status
        ).scalar() or Decimal("0")
        
        pipeline.append({
            "status": status,
            "count": count,
            "total_value": float(total_value)
        })
    
    # Won/Lost stats
    won_count = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "WON"
    ).scalar() or 0
    
    lost_count = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "LOST"
    ).scalar() or 0
    
    return {
        "pipeline": pipeline,
        "won": won_count,
        "lost": lost_count,
        "win_rate": round(won_count / (won_count + lost_count) * 100, 2) if (won_count + lost_count) > 0 else 0
    }
