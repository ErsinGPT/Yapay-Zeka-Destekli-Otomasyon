"""
CRM Models - Customer, Opportunity, Quote, Project
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class OpportunityStatus(enum.Enum):
    """Opportunity/Lead status"""
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


class ProjectStatus(enum.Enum):
    """Waterfall project lifecycle statuses"""
    OPPORTUNITY = "OPPORTUNITY"
    WON = "WON"
    ENGINEERING = "ENGINEERING"
    PROCUREMENT = "PROCUREMENT"
    ASSEMBLY = "ASSEMBLY"
    TESTING = "TESTING"
    SHIPPING = "SHIPPING"
    COMMISSIONING = "COMMISSIONING"
    COMPLETED = "COMPLETED"
    INVOICED = "INVOICED"


class Currency(enum.Enum):
    """Supported currencies"""
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"


class Customer(Base):
    """Customer/Client model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))  # English name for export docs
    
    # Contact info
    email = Column(String(255))
    phone = Column(String(50))
    contact_person = Column(String(255))
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100), default="Türkiye")
    postal_code = Column(String(20))
    
    # Tax info
    tax_office = Column(String(255))
    tax_id = Column(String(50))  # Vergi No
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="customer")
    projects = relationship("Project", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.name}>"


class Opportunity(Base):
    """Sales opportunity/lead"""
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Value
    expected_revenue = Column(Numeric(15, 2))
    currency = Column(String(3), default="TRY")
    
    # Status
    status = Column(String(20), default=OpportunityStatus.NEW.value)
    probability = Column(Integer, default=50)  # 0-100%
    
    # Dates
    expected_close_date = Column(DateTime(timezone=True))
    closed_date = Column(DateTime(timezone=True))
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    quotes = relationship("Quote", back_populates="opportunity")
    project = relationship("Project", back_populates="opportunity", uselist=False)
    
    def __repr__(self):
        return f"<Opportunity {self.title}>"


class Quote(Base):
    """Quote/Proposal for an opportunity"""
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    
    version = Column(Integer, default=1)  # Quote versioning
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    discount = Column(Numeric(15, 2), default=0)
    tax = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), nullable=False)
    
    currency = Column(String(3), default="TRY")
    exchange_rate = Column(Numeric(10, 4), default=1)  # At quote time
    
    # Status
    is_accepted = Column(Boolean, default=False)
    
    # Dates
    valid_until = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="quotes")
    
    def __repr__(self):
        return f"<Quote {self.opportunity_id}-v{self.version}>"


class Project(Base):
    """Main Project model - heart of the system"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique project code: PRJ-YYYY-XXXX
    project_code = Column(String(20), unique=True, index=True, nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Relations
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    
    # Waterfall Status
    status = Column(String(20), default=ProjectStatus.WON.value)
    
    # Financial
    contract_amount = Column(Numeric(15, 2))
    currency = Column(String(3), default="TRY")
    exchange_rate_at_start = Column(Numeric(10, 4))  # Kur koruması için
    
    # Project Manager
    manager_id = Column(Integer, ForeignKey("users.id"))
    
    # Dates
    start_date = Column(DateTime(timezone=True))
    expected_end_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="projects")
    opportunity = relationship("Opportunity", back_populates="project")
    stock_movements = relationship("StockMovement", back_populates="project")
    stock_reservations = relationship("StockReservation", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
    expenses = relationship("Expense", back_populates="project")
    service_forms = relationship("ServiceForm", back_populates="project")
    delivery_notes = relationship("DeliveryNote", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.project_code}>"
