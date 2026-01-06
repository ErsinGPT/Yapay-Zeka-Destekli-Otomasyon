"""
Warehouse and Stock Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class WarehouseType(enum.Enum):
    """Warehouse types"""
    PHYSICAL = "PHYSICAL"  # Ana depo, Yan depo
    VIRTUAL = "VIRTUAL"    # Teknik servis araçları


class MovementType(enum.Enum):
    """Stock movement types"""
    IN = "IN"                    # Satın alma girişi
    OUT = "OUT"                  # Satış çıkışı
    TRANSFER = "TRANSFER"        # Depolar arası transfer
    ADJUSTMENT = "ADJUSTMENT"    # Sayım düzeltme
    PRODUCTION = "PRODUCTION"    # Üretimden giriş
    CONSUMPTION = "CONSUMPTION"  # Üretimde kullanım
    SERVICE = "SERVICE"          # Servis formu ile çıkış


class ReservationStatus(enum.Enum):
    """Stock reservation status"""
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class Warehouse(Base):
    """Warehouse/Depot model - Physical and Virtual (Vehicle)"""
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)  # DEPO-01, ARAC-34AB123
    
    warehouse_type = Column(String(20), default=WarehouseType.PHYSICAL.value)
    
    # For virtual warehouses (vehicles)
    vehicle_plate = Column(String(20))  # 34 AB 123
    driver_id = Column(Integer, ForeignKey("users.id"))
    
    # Address (for physical)
    address = Column(Text)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    warehouse_stocks = relationship("WarehouseStock", back_populates="warehouse")
    movements_from = relationship(
        "StockMovement",
        foreign_keys="StockMovement.from_warehouse_id",
        back_populates="from_warehouse"
    )
    movements_to = relationship(
        "StockMovement",
        foreign_keys="StockMovement.to_warehouse_id",
        back_populates="to_warehouse"
    )
    service_forms = relationship("ServiceForm", back_populates="vehicle_warehouse")
    
    def __repr__(self):
        return f"<Warehouse {self.code}: {self.name}>"


class WarehouseStock(Base):
    """Stock levels per warehouse-product combination"""
    __tablename__ = "warehouse_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Stock quantities
    quantity = Column(Numeric(15, 3), default=0)  # Physical stock
    reserved_quantity = Column(Numeric(15, 3), default=0)  # Reserved for projects
    
    # Available = quantity - reserved_quantity
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="warehouse_stocks")
    product = relationship("Product", back_populates="warehouse_stocks")
    
    def __repr__(self):
        return f"<WarehouseStock {self.warehouse_id}-{self.product_id}: {self.quantity}>"
    
    @property
    def available_quantity(self):
        """Calculate available (non-reserved) quantity"""
        return self.quantity - (self.reserved_quantity or 0)


class StockMovement(Base):
    """Stock movement/transaction log"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Optional: movements can be linked to a project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Movement type
    movement_type = Column(String(20), nullable=False)
    
    # Warehouses
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    
    # Quantity (always positive, direction determined by from/to)
    quantity = Column(Numeric(15, 3), nullable=False)
    
    # Unit cost at time of movement
    unit_cost = Column(Numeric(15, 4))
    
    # Reference document
    reference_type = Column(String(50))  # invoice, service_form, transfer_note
    reference_id = Column(Integer)
    
    notes = Column(Text)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")
    from_warehouse = relationship(
        "Warehouse",
        foreign_keys=[from_warehouse_id],
        back_populates="movements_from"
    )
    to_warehouse = relationship(
        "Warehouse",
        foreign_keys=[to_warehouse_id],
        back_populates="movements_to"
    )
    
    def __repr__(self):
        return f"<StockMovement {self.movement_type}: {self.product_id} x{self.quantity}>"


class StockReservation(Base):
    """Stock reservation for projects"""
    __tablename__ = "stock_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    
    quantity = Column(Numeric(15, 3), nullable=False)
    
    status = Column(String(20), default=ReservationStatus.ACTIVE.value)
    
    notes = Column(Text)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fulfilled_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("Project", back_populates="stock_reservations")
    product = relationship("Product", back_populates="stock_reservations")
    
    def __repr__(self):
        return f"<StockReservation {self.project_id}: {self.product_id} x{self.quantity}>"
