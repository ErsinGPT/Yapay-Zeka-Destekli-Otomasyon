"""
Product and BOM Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductCategory(Base):
    """Product category for organization"""
    __tablename__ = "product_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    parent_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # Relationships
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<ProductCategory {self.name}>"


class Product(Base):
    """Product/Stock Card model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    sku = Column(String(50), unique=True, index=True, nullable=False)  # Stock Keeping Unit
    barcode = Column(String(50), index=True)  # Barkod/QR
    
    # Names
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))  # English name for export invoices
    description = Column(Text)
    
    # Category
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # Export requirements
    gtip_code = Column(String(20))  # Gümrük Tarife İstatistik Pozisyonu
    
    # Unit
    unit = Column(String(20), default="Adet")  # Adet, Kg, Metre, Set
    
    # Pricing
    cost = Column(Numeric(15, 4), default=0)  # Maliyet
    list_price = Column(Numeric(15, 2), default=0)  # Liste fiyatı
    currency = Column(String(3), default="TRY")
    
    # Stock settings
    min_stock_level = Column(Integer, default=0)  # Kritik stok seviyesi
    is_stockable = Column(Boolean, default=True)  # Stok takibi yapılsın mı
    is_purchasable = Column(Boolean, default=True)
    is_sellable = Column(Boolean, default=True)
    
    # BOM - Is this a manufactured/assembled product?
    is_bom = Column(Boolean, default=False)  # Set ürün (Pano gibi)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    warehouse_stocks = relationship("WarehouseStock", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    stock_reservations = relationship("StockReservation", back_populates="product")
    invoice_items = relationship("InvoiceItem", back_populates="product")
    
    # BOM relationships
    bom_items_as_parent = relationship(
        "BOMItem", 
        foreign_keys="BOMItem.parent_product_id",
        back_populates="parent_product"
    )
    bom_items_as_child = relationship(
        "BOMItem",
        foreign_keys="BOMItem.child_product_id", 
        back_populates="child_product"
    )
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"


class BOMItem(Base):
    """Bill of Materials - Component relationships"""
    __tablename__ = "bom_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Parent product (e.g., Otomasyon Panosu)
    parent_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Child component (e.g., PLC, Röle)
    child_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Quantity needed
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    
    # Optional notes
    notes = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent_product = relationship(
        "Product", 
        foreign_keys=[parent_product_id],
        back_populates="bom_items_as_parent"
    )
    child_product = relationship(
        "Product",
        foreign_keys=[child_product_id],
        back_populates="bom_items_as_child"
    )
    
    def __repr__(self):
        return f"<BOMItem {self.parent_product_id} -> {self.child_product_id} x{self.quantity}>"
