"""
Expense Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Expense(Base):
    """Personnel expense entry"""
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # MANDATORY: Every expense must be linked to a project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Expense type
    expense_type = Column(String(50), nullable=False)  # TRAVEL, ACCOMMODATION, FOOD, TRANSPORT, OTHER
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="TRY")
    
    # Description
    description = Column(Text, nullable=False)
    
    # Receipt/Document
    receipt_url = Column(String(500))  # File path or URL
    receipt_date = Column(DateTime(timezone=True))
    
    # Approval workflow
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="expenses")
    user = relationship("User", foreign_keys=[user_id], back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense {self.expense_type}: {self.amount}>"


class PersonnelAccount(Base):
    """Personnel current account (Cari Hesap)"""
    __tablename__ = "personnel_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Balance (positive = company owes employee)
    balance = Column(Numeric(15, 2), default=0)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personnel_account")
    transactions = relationship("AccountTransaction", back_populates="account")
    
    def __repr__(self):
        return f"<PersonnelAccount {self.user_id}: {self.balance}>"


class AccountTransaction(Base):
    """Personnel account transactions"""
    __tablename__ = "account_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    account_id = Column(Integer, ForeignKey("personnel_accounts.id"), nullable=False)
    
    # Transaction type
    transaction_type = Column(String(20), nullable=False)  # DEBIT (borç), CREDIT (alacak)
    
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Reference to expense (if applicable)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    account = relationship("PersonnelAccount", back_populates="transactions")
    
    def __repr__(self):
        return f"<AccountTransaction {self.transaction_type}: {self.amount}>"
