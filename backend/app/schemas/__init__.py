"""
CRM Pydantic Schemas
Request and Response models for Customer, Opportunity, Quote, Project
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ===== CUSTOMER SCHEMAS =====

class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str
    name_en: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Türkiye"
    postal_code: Optional[str] = None
    tax_office: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Create customer request"""
    pass


class CustomerUpdate(BaseModel):
    """Update customer request - all fields optional"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    tax_office: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """Customer response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== OPPORTUNITY SCHEMAS =====

class OpportunityBase(BaseModel):
    """Base opportunity schema"""
    title: str
    description: Optional[str] = None
    customer_id: int
    expected_revenue: Optional[Decimal] = None
    currency: str = "TRY"
    probability: int = 50
    expected_close_date: Optional[datetime] = None


class OpportunityCreate(OpportunityBase):
    """Create opportunity request"""
    assigned_to: Optional[int] = None


class OpportunityUpdate(BaseModel):
    """Update opportunity request"""
    title: Optional[str] = None
    description: Optional[str] = None
    expected_revenue: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class OpportunityResponse(OpportunityBase):
    """Opportunity response"""
    id: int
    status: str
    closed_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested customer info
    customer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== QUOTE SCHEMAS =====

class QuoteBase(BaseModel):
    """Base quote schema"""
    subtotal: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal
    currency: str = "TRY"
    exchange_rate: Decimal = Decimal("1")
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class QuoteCreate(QuoteBase):
    """Create quote request"""
    pass


class QuoteResponse(QuoteBase):
    """Quote response"""
    id: int
    opportunity_id: int
    version: int
    is_accepted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== PROJECT SCHEMAS =====

class ProjectBase(BaseModel):
    """Base project schema"""
    title: str
    description: Optional[str] = None
    contract_amount: Optional[Decimal] = None
    currency: str = "TRY"
    start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Create project from opportunity"""
    customer_id: int
    opportunity_id: Optional[int] = None
    manager_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """Update project request"""
    title: Optional[str] = None
    description: Optional[str] = None
    contract_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    manager_id: Optional[int] = None
    start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ProjectStatusUpdate(BaseModel):
    """Update project status"""
    status: str


class ProjectResponse(ProjectBase):
    """Project response"""
    id: int
    project_code: str
    customer_id: int
    opportunity_id: Optional[int] = None
    status: str
    manager_id: Optional[int] = None
    exchange_rate_at_start: Optional[Decimal] = None
    actual_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested info
    customer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProjectSummary(BaseModel):
    """Project profitability summary"""
    project_id: int
    project_code: str
    revenue: Decimal
    material_cost: Decimal
    labor_cost: Decimal
    expenses: Decimal
    net_profit: Decimal
    profit_margin: float  # Percentage
