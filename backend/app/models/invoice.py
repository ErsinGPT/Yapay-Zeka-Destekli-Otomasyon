"""
Invoice Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Invoice(Base):
    """Invoice model - Domestic and Export"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice number (auto-generated or manual)
    invoice_number = Column(String(50), unique=True, index=True)
    
    # MANDATORY: Every invoice must be linked to a project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Type: DOMESTIC or EXPORT
    invoice_type = Column(String(20), default="DOMESTIC")
    
    # Dates
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True))
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    discount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)  # KDV
    total = Column(Numeric(15, 2), nullable=False)
    
    # Currency
    currency = Column(String(3), default="TRY")
    exchange_rate = Column(Numeric(10, 4), default=1)  # Invoice time rate
    
    # VAT Rate (0% for export)
    vat_rate = Column(Numeric(5, 2), default=20.00)
    
    # Status
    status = Column(String(20), default="DRAFT")  # DRAFT, SENT, PAID, CANCELLED
    
    # e-Invoice
    e_invoice_uuid = Column(String(100))
    e_invoice_status = Column(String(50))
    
    notes = Column(Text)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"


class InvoiceItem(Base):
    """Invoice line items"""
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Description (can override product name)
    description = Column(String(500), nullable=False)
    description_en = Column(String(500))  # REQUIRED for export
    
    # Export requirement
    gtip_code = Column(String(20))  # REQUIRED for export
    
    # Quantities and pricing
    quantity = Column(Numeric(15, 3), nullable=False)
    unit = Column(String(20), default="Adet")
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount = Column(Numeric(15, 2), default=0)
    
    # Tax
    vat_rate = Column(Numeric(5, 2), default=20.00)
    vat_amount = Column(Numeric(15, 2), default=0)
    
    # Total = (quantity * unit_price) - discount + vat_amount
    total = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")
    
    def __repr__(self):
        return f"<InvoiceItem {self.description[:30]}>"
