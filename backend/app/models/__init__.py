"""
Models Package - Import all models for easy access
"""
from app.models.user import User, Role
from app.models.project import Customer, Opportunity, Quote, Project, OpportunityStatus, ProjectStatus, Currency
from app.models.product import Product, ProductCategory, BOMItem
from app.models.warehouse import Warehouse, WarehouseStock, StockMovement, StockReservation, WarehouseType, MovementType, ReservationStatus
from app.models.invoice import Invoice, InvoiceItem
from app.models.expense import Expense, PersonnelAccount, AccountTransaction
from app.models.service_form import ServiceForm, ServiceFormItem, DeliveryNote, DeliveryNoteItem
from app.models.currency import CurrencyRate


__all__ = [
    # User & Auth
    "User",
    "Role",
    
    # CRM
    "Customer",
    "Opportunity",
    "Quote",
    "Project",
    "OpportunityStatus",
    "ProjectStatus",
    "Currency",
    
    # Inventory
    "Product",
    "ProductCategory", 
    "BOMItem",
    "Warehouse",
    "WarehouseStock",
    "StockMovement",
    "StockReservation",
    "WarehouseType",
    "MovementType",
    "ReservationStatus",
    
    # Finance
    "Invoice",
    "InvoiceItem",
    "Expense",
    "PersonnelAccount",
    "AccountTransaction",
    "CurrencyRate",
    
    # Operations
    "ServiceForm",
    "ServiceFormItem",
    "DeliveryNote",
    "DeliveryNoteItem",
]
