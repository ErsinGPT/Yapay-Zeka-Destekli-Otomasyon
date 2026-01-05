"""
Expenses Router
Handles personnel expense management and approval workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

router = APIRouter()

# Expense types
EXPENSE_TYPES = ["TRAVEL", "ACCOMMODATION", "FOOD", "TRANSPORT", "OTHER"]
EXPENSE_STATUSES = ["PENDING", "APPROVED", "REJECTED"]


@router.get("/")
async def get_expenses(db: Session = Depends(get_db)):
    """Get all expenses (filtered by user role)"""
    # TODO: Implement with role-based filtering
    return []


@router.post("/")
async def create_expense(db: Session = Depends(get_db)):
    """
    Create new expense entry.
    Required: expense_type, amount, project_id, receipt photo
    """
    # TODO: Implement with file upload
    return {"message": "Expense created", "id": 1}


@router.get("/{expense_id}")
async def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get expense details"""
    # TODO: Implement
    return {"id": expense_id}


@router.put("/{expense_id}")
async def update_expense(expense_id: int, db: Session = Depends(get_db)):
    """Update expense (only if PENDING status)"""
    # TODO: Implement
    return {"message": "Expense updated"}


@router.post("/{expense_id}/approve")
async def approve_expense(expense_id: int, db: Session = Depends(get_db)):
    """
    Approve expense.
    When approved, creates automatic CREDIT entry in personnel account.
    """
    # TODO: Implement with personnel account integration
    return {"message": "Expense approved"}


@router.post("/{expense_id}/reject")
async def reject_expense(expense_id: int, db: Session = Depends(get_db)):
    """Reject expense with reason"""
    # TODO: Implement
    return {"message": "Expense rejected"}


@router.get("/personnel/{user_id}/account")
async def get_personnel_account(user_id: int, db: Session = Depends(get_db)):
    """
    Get personnel current account (cari hesap).
    Shows balance and transaction history.
    """
    # TODO: Implement
    return {
        "user_id": user_id,
        "balance": 0,
        "transactions": []
    }
