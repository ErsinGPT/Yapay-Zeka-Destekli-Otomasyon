"""
Expenses Router
Handles personnel expense management and approval workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import os

from app.database import get_db
from app.models import Expense, PersonnelAccount, AccountTransaction, Project, User
from app.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseApproval,
    PersonnelAccountResponse, AccountTransactionResponse
)
from app.routers.auth import get_current_user
from app.config import settings

router = APIRouter()

# Expense types and statuses
EXPENSE_TYPES = ["TRAVEL", "ACCOMMODATION", "FOOD", "TRANSPORT", "MATERIAL", "OTHER"]
EXPENSE_STATUSES = ["PENDING", "APPROVED", "REJECTED"]


@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    project_id: Optional[int] = None,
    user_id: Optional[int] = None,
    expense_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all expenses (filtered by user role)"""
    query = db.query(Expense)
    
    # Role-based filtering: regular users see only their expenses
    # Admin/Manager can see all
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        query = query.filter(Expense.user_id == current_user.id)
    elif user_id:
        query = query.filter(Expense.user_id == user_id)
    
    if project_id:
        query = query.filter(Expense.project_id == project_id)
    
    if expense_type:
        query = query.filter(Expense.expense_type == expense_type)
    
    if status:
        query = query.filter(Expense.status == status)
    
    expenses = query.order_by(Expense.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for exp in expenses:
        user = db.query(User).filter(User.id == exp.user_id).first()
        project = db.query(Project).filter(Project.id == exp.project_id).first()
        
        result.append({
            **exp.__dict__,
            "user_name": user.full_name if user else None,
            "project_code": project.project_code if project else None
        })
    
    return result


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create new expense entry.
    Required: expense_type, amount, project_id
    """
    # Validate project
    project = db.query(Project).filter(Project.id == expense_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    
    # Validate expense type
    if expense_data.expense_type not in EXPENSE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Geçersiz masraf tipi. İzin verilen: {EXPENSE_TYPES}"
        )
    
    db_expense = Expense(
        user_id=current_user.id,
        status="PENDING",
        **expense_data.model_dump()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return {
        **db_expense.__dict__,
        "user_name": current_user.full_name,
        "project_code": project.project_code
    }


@router.get("/types")
async def get_expense_types():
    """Get available expense types"""
    return {
        "types": EXPENSE_TYPES,
        "descriptions": {
            "TRAVEL": "Seyahat",
            "ACCOMMODATION": "Konaklama",
            "FOOD": "Yemek",
            "TRANSPORT": "Ulaşım",
            "MATERIAL": "Malzeme",
            "OTHER": "Diğer"
        }
    }


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense details"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    # Check access
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        if expense.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Bu masrafa erişim yetkiniz yok")
    
    user = db.query(User).filter(User.id == expense.user_id).first()
    project = db.query(Project).filter(Project.id == expense.project_id).first()
    
    return {
        **expense.__dict__,
        "user_name": user.full_name if user else None,
        "project_code": project.project_code if project else None
    }


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense (only if PENDING status)"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    # Only owner can update
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece kendi masraflarınızı güncelleyebilirsiniz")
    
    if expense.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen masraflar güncellenebilir")
    
    update_data = expense_update.model_dump(exclude_unset=True)
    
    # Validate expense type if provided
    if "expense_type" in update_data and update_data["expense_type"] not in EXPENSE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Geçersiz masraf tipi. İzin verilen: {EXPENSE_TYPES}"
        )
    
    for key, value in update_data.items():
        setattr(expense, key, value)
    
    db.commit()
    db.refresh(expense)
    
    user = db.query(User).filter(User.id == expense.user_id).first()
    project = db.query(Project).filter(Project.id == expense.project_id).first()
    
    return {
        **expense.__dict__,
        "user_name": user.full_name if user else None,
        "project_code": project.project_code if project else None
    }


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete expense (only if PENDING status)"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    # Only owner can delete
    if expense.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Sadece kendi masraflarınızı silebilirsiniz")
    
    if expense.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen masraflar silinebilir")
    
    db.delete(expense)
    db.commit()


@router.post("/{expense_id}/approve")
async def approve_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Approve expense.
    When approved, creates automatic CREDIT entry in personnel account.
    """
    # Check permission
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Masraf onaylama yetkiniz yok")
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    if expense.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen masraflar onaylanabilir")
    
    # Get or create personnel account
    account = db.query(PersonnelAccount).filter(
        PersonnelAccount.user_id == expense.user_id
    ).first()
    
    if not account:
        account = PersonnelAccount(
            user_id=expense.user_id,
            balance=Decimal("0")
        )
        db.add(account)
        db.flush()
    
    # Create credit transaction
    transaction = AccountTransaction(
        account_id=account.id,
        transaction_type="CREDIT",
        amount=expense.amount,
        expense_id=expense.id,
        description=f"Masraf onayı: {expense.description}"
    )
    db.add(transaction)
    
    # Update account balance
    account.balance += expense.amount
    
    # Update expense
    expense.status = "APPROVED"
    expense.approved_by = current_user.id
    expense.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Masraf onaylandı",
        "expense_id": expense.id,
        "amount": float(expense.amount),
        "new_balance": float(account.balance)
    }


@router.post("/{expense_id}/reject")
async def reject_expense(
    expense_id: int,
    rejection: ExpenseApproval,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reject expense with reason"""
    # Check permission
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Masraf reddetme yetkiniz yok")
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    if expense.status != "PENDING":
        raise HTTPException(status_code=400, detail="Sadece bekleyen masraflar reddedilebilir")
    
    expense.status = "REJECTED"
    expense.approved_by = current_user.id
    expense.approved_at = datetime.utcnow()
    expense.rejection_reason = rejection.rejection_reason
    
    db.commit()
    
    return {
        "message": "Masraf reddedildi",
        "expense_id": expense.id,
        "rejection_reason": rejection.rejection_reason
    }


@router.post("/{expense_id}/upload-receipt")
async def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload receipt for expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Masraf bulunamadı")
    
    if expense.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece kendi masraflarınıza belge yükleyebilirsiniz")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Geçersiz dosya tipi. İzin verilen: JPG, PNG, PDF")
    
    # Save file
    receipts_dir = os.path.join(settings.UPLOAD_DIR, "receipts")
    os.makedirs(receipts_dir, exist_ok=True)
    
    file_ext = file.filename.split(".")[-1]
    filename = f"expense_{expense_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
    file_path = os.path.join(receipts_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    expense.receipt_url = f"/uploads/receipts/{filename}"
    db.commit()
    
    return {
        "message": "Belge yüklendi",
        "receipt_url": expense.receipt_url
    }


# ===== PERSONNEL ACCOUNT ENDPOINTS =====

@router.get("/personnel/{user_id}/account", response_model=PersonnelAccountResponse)
async def get_personnel_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get personnel current account (cari hesap).
    Shows balance and transaction history.
    """
    # Check access
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Bu hesaba erişim yetkiniz yok")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    account = db.query(PersonnelAccount).filter(PersonnelAccount.user_id == user_id).first()
    
    if not account:
        # Return empty account
        return {
            "id": 0,
            "user_id": user_id,
            "user_name": user.full_name,
            "balance": Decimal("0"),
            "updated_at": None
        }
    
    return {
        "id": account.id,
        "user_id": account.user_id,
        "user_name": user.full_name,
        "balance": account.balance,
        "updated_at": account.updated_at
    }


@router.get("/personnel/{user_id}/transactions", response_model=List[AccountTransactionResponse])
async def get_personnel_transactions(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get personnel account transactions"""
    # Check access
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Bu hesaba erişim yetkiniz yok")
    
    account = db.query(PersonnelAccount).filter(PersonnelAccount.user_id == user_id).first()
    
    if not account:
        return []
    
    transactions = db.query(AccountTransaction).filter(
        AccountTransaction.account_id == account.id
    ).order_by(AccountTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return transactions


@router.post("/personnel/{user_id}/payment")
async def record_payment(
    user_id: int,
    amount: Decimal,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record payment to personnel (reduces balance)"""
    # Check permission
    if not current_user.is_superuser and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Ödeme kaydetme yetkiniz yok")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    # Get or create account
    account = db.query(PersonnelAccount).filter(PersonnelAccount.user_id == user_id).first()
    if not account:
        account = PersonnelAccount(user_id=user_id, balance=Decimal("0"))
        db.add(account)
        db.flush()
    
    # Create debit transaction
    transaction = AccountTransaction(
        account_id=account.id,
        transaction_type="DEBIT",
        amount=amount,
        description=description or "Ödeme"
    )
    db.add(transaction)
    
    # Update balance
    account.balance -= amount
    
    db.commit()
    
    return {
        "message": "Ödeme kaydedildi",
        "amount": float(amount),
        "new_balance": float(account.balance)
    }
