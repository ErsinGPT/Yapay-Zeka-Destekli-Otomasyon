"""
Service Form and Delivery Note Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ServiceForm(Base):
    """Technical service form for field operations"""
    __tablename__ = "service_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Form number
    form_number = Column(String(50), unique=True, index=True)
    
    # Links
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    vehicle_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))  # Araç deposu
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, COMPLETED
    
    # Work details
    work_description = Column(Text)
    work_performed = Column(Text)
    
    # Customer signature
    customer_signed = Column(Boolean, default=False)
    customer_name = Column(String(255))
    signature_url = Column(String(500))
    
    # Dates
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="service_forms")
    vehicle_warehouse = relationship("Warehouse", back_populates="service_forms")
    technician = relationship("User", back_populates="service_forms")
    items = relationship("ServiceFormItem", back_populates="service_form", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ServiceForm {self.form_number}>"


class ServiceFormItem(Base):
    """Materials used in service form"""
    __tablename__ = "service_form_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    service_form_id = Column(Integer, ForeignKey("service_forms.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Numeric(15, 3), nullable=False)
    
    # True = delivered to customer (leaves inventory)
    # False = returned to warehouse
    delivered_to_customer = Column(Boolean, default=True)
    
    notes = Column(String(255))
    
    # Relationships
    service_form = relationship("ServiceForm", back_populates="items")
    
    def __repr__(self):
        return f"<ServiceFormItem {self.product_id} x{self.quantity}>"


class DeliveryNote(Base):
    """Internal delivery note (Dahili İrsaliye)"""
    __tablename__ = "delivery_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Note number
    note_number = Column(String(50), unique=True, index=True)
    
    # Links
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    # Status
    status = Column(String(20), default="PENDING")  # PENDING, IN_TRANSIT, DELIVERED
    
    # PDF document
    pdf_url = Column(String(500))
    
    # Dates
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Personnel
    shipped_by = Column(Integer, ForeignKey("users.id"))
    received_by = Column(Integer, ForeignKey("users.id"))
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="delivery_notes")
    items = relationship("DeliveryNoteItem", back_populates="delivery_note", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DeliveryNote {self.note_number}>"


class DeliveryNoteItem(Base):
    """Items in delivery note"""
    __tablename__ = "delivery_note_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    delivery_note_id = Column(Integer, ForeignKey("delivery_notes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Numeric(15, 3), nullable=False)
    
    notes = Column(String(255))
    
    # Relationships
    delivery_note = relationship("DeliveryNote", back_populates="items")
    
    def __repr__(self):
        return f"<DeliveryNoteItem {self.product_id} x{self.quantity}>"
