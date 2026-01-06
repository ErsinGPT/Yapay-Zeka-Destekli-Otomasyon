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


# ===== PRODUCT SCHEMAS =====

class ProductCategoryBase(BaseModel):
    """Base product category schema"""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class ProductCategoryCreate(ProductCategoryBase):
    """Create product category request"""
    pass


class ProductCategoryResponse(ProductCategoryBase):
    """Product category response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    """Base product schema"""
    sku: str
    name: str
    barcode: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    gtip_code: Optional[str] = None
    unit: str = "Adet"
    cost: Decimal = Decimal("0")
    list_price: Decimal = Decimal("0")
    currency: str = "TRY"
    min_stock_level: int = 0
    is_stockable: bool = True
    is_purchasable: bool = True
    is_sellable: bool = True
    is_bom: bool = False


class ProductCreate(ProductBase):
    """Create product request"""
    pass


class ProductUpdate(BaseModel):
    """Update product request"""
    sku: Optional[str] = None
    name: Optional[str] = None
    barcode: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    gtip_code: Optional[str] = None
    unit: Optional[str] = None
    cost: Optional[Decimal] = None
    list_price: Optional[Decimal] = None
    currency: Optional[str] = None
    min_stock_level: Optional[int] = None
    is_stockable: Optional[bool] = None
    is_purchasable: Optional[bool] = None
    is_sellable: Optional[bool] = None
    is_bom: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed stock info
    total_stock: Optional[Decimal] = None
    available_stock: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class BOMItemBase(BaseModel):
    """Base BOM item schema"""
    child_product_id: int
    quantity: Decimal = Decimal("1")
    notes: Optional[str] = None


class BOMItemCreate(BOMItemBase):
    """Create BOM item"""
    pass


class BOMItemResponse(BOMItemBase):
    """BOM item response"""
    id: int
    parent_product_id: int
    child_product_name: Optional[str] = None
    child_product_sku: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== WAREHOUSE SCHEMAS =====

class WarehouseBase(BaseModel):
    """Base warehouse schema"""
    name: str
    code: str
    warehouse_type: str = "PHYSICAL"
    vehicle_plate: Optional[str] = None
    driver_id: Optional[int] = None
    address: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    """Create warehouse request"""
    pass


class WarehouseUpdate(BaseModel):
    """Update warehouse request"""
    name: Optional[str] = None
    code: Optional[str] = None
    warehouse_type: Optional[str] = None
    vehicle_plate: Optional[str] = None
    driver_id: Optional[int] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase):
    """Warehouse response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class WarehouseStockResponse(BaseModel):
    """Warehouse stock level"""
    id: int
    warehouse_id: int
    product_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal
    
    model_config = ConfigDict(from_attributes=True)


# ===== STOCK SCHEMAS =====

class StockTransferRequest(BaseModel):
    """Stock transfer between warehouses"""
    project_id: int
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: Decimal
    notes: Optional[str] = None


class StockReservationCreate(BaseModel):
    """Create stock reservation"""
    project_id: int
    product_id: int
    warehouse_id: int
    quantity: Decimal
    notes: Optional[str] = None


class StockReservationResponse(BaseModel):
    """Stock reservation response"""
    id: int
    project_id: int
    product_id: int
    warehouse_id: int
    quantity: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    fulfilled_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class StockMovementCreate(BaseModel):
    """Create manual stock movement"""
    project_id: int
    product_id: int
    movement_type: str
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class StockMovementResponse(BaseModel):
    """Stock movement response"""
    id: int
    project_id: int
    product_id: int
    product_name: Optional[str] = None
    movement_type: str
    from_warehouse_id: Optional[int] = None
    to_warehouse_id: Optional[int] = None
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== INVOICE SCHEMAS =====

class InvoiceItemBase(BaseModel):
    """Base invoice item schema"""
    product_id: Optional[int] = None
    description: str
    description_en: Optional[str] = None
    gtip_code: Optional[str] = None
    quantity: Decimal
    unit: str = "Adet"
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    vat_rate: Decimal = Decimal("20.00")


class InvoiceItemCreate(InvoiceItemBase):
    """Create invoice item"""
    pass


class InvoiceItemResponse(InvoiceItemBase):
    """Invoice item response"""
    id: int
    invoice_id: int
    vat_amount: Decimal
    total: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    """Base invoice schema"""
    project_id: int
    customer_id: int
    invoice_type: str = "DOMESTIC"
    invoice_date: datetime
    due_date: Optional[datetime] = None
    currency: str = "TRY"
    exchange_rate: Decimal = Decimal("1")
    vat_rate: Decimal = Decimal("20.00")
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Create invoice request"""
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    """Update invoice request"""
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Invoice response"""
    id: int
    invoice_number: str
    subtotal: Decimal
    discount: Decimal
    tax_amount: Decimal
    total: Decimal
    status: str
    e_invoice_uuid: Optional[str] = None
    e_invoice_status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested
    items: List[InvoiceItemResponse] = []
    customer_name: Optional[str] = None
    project_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== EXPENSE SCHEMAS =====

class ExpenseBase(BaseModel):
    """Base expense schema"""
    project_id: int
    expense_type: str
    amount: Decimal
    currency: str = "TRY"
    description: str
    receipt_date: Optional[datetime] = None


class ExpenseCreate(ExpenseBase):
    """Create expense request"""
    pass


class ExpenseUpdate(BaseModel):
    """Update expense request"""
    expense_type: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    receipt_date: Optional[datetime] = None


class ExpenseResponse(ExpenseBase):
    """Expense response"""
    id: int
    user_id: int
    status: str
    receipt_url: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested
    user_name: Optional[str] = None
    project_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ExpenseApproval(BaseModel):
    """Expense approval/rejection"""
    rejection_reason: Optional[str] = None


class PersonnelAccountResponse(BaseModel):
    """Personnel account response"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    balance: Decimal
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class AccountTransactionResponse(BaseModel):
    """Account transaction response"""
    id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    expense_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== SERVICE FORM SCHEMAS =====

class ServiceFormItemBase(BaseModel):
    """Base service form item schema"""
    product_id: int
    quantity: Decimal
    delivered_to_customer: bool = True
    notes: Optional[str] = None


class ServiceFormItemCreate(ServiceFormItemBase):
    """Create service form item"""
    pass


class ServiceFormItemResponse(ServiceFormItemBase):
    """Service form item response"""
    id: int
    service_form_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ServiceFormBase(BaseModel):
    """Base service form schema"""
    project_id: int
    vehicle_warehouse_id: Optional[int] = None
    work_description: Optional[str] = None
    notes: Optional[str] = None


class ServiceFormCreate(ServiceFormBase):
    """Create service form request"""
    pass


class ServiceFormUpdate(BaseModel):
    """Update service form request"""
    vehicle_warehouse_id: Optional[int] = None
    work_description: Optional[str] = None
    work_performed: Optional[str] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None


class ServiceFormComplete(BaseModel):
    """Complete service form request"""
    work_performed: str
    customer_name: str
    customer_signed: bool = True


class ServiceFormResponse(ServiceFormBase):
    """Service form response"""
    id: int
    form_number: str
    technician_id: int
    status: str
    work_performed: Optional[str] = None
    customer_signed: bool
    customer_name: Optional[str] = None
    signature_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested
    items: List[ServiceFormItemResponse] = []
    project_code: Optional[str] = None
    technician_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== DELIVERY NOTE SCHEMAS =====

class DeliveryNoteItemBase(BaseModel):
    """Base delivery note item schema"""
    product_id: int
    quantity: Decimal
    notes: Optional[str] = None


class DeliveryNoteItemCreate(DeliveryNoteItemBase):
    """Create delivery note item"""
    pass


class DeliveryNoteItemResponse(DeliveryNoteItemBase):
    """Delivery note item response"""
    id: int
    delivery_note_id: int
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DeliveryNoteBase(BaseModel):
    """Base delivery note schema"""
    project_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    notes: Optional[str] = None


class DeliveryNoteCreate(DeliveryNoteBase):
    """Create delivery note request"""
    items: List[DeliveryNoteItemCreate]


class DeliveryNoteUpdate(BaseModel):
    """Update delivery note request"""
    notes: Optional[str] = None


class DeliveryNoteResponse(DeliveryNoteBase):
    """Delivery note response"""
    id: int
    note_number: str
    status: str
    pdf_url: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    shipped_by: Optional[int] = None
    received_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested
    items: List[DeliveryNoteItemResponse] = []
    project_code: Optional[str] = None
    from_warehouse_name: Optional[str] = None
    to_warehouse_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== SETTINGS SCHEMAS =====

class CompanySettings(BaseModel):
    """Company settings"""
    company_name: str = "Otomasyon A.Ş."
    company_name_en: Optional[str] = None
    tax_office: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class InvoiceNumberingSettings(BaseModel):
    """Invoice numbering settings"""
    prefix: str = "FTR"
    year_format: str = "%Y"
    separator: str = "-"
    padding: int = 6
    next_number: int = 1


class AppSettings(BaseModel):
    """Application settings"""
    company: CompanySettings = CompanySettings()
    invoice_numbering: InvoiceNumberingSettings = InvoiceNumberingSettings()
    default_currency: str = "TRY"
    default_vat_rate: Decimal = Decimal("20.00")


# ===== REPORT SCHEMAS =====

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_projects: int = 0
    active_projects: int = 0
    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    pending_invoices: int = 0
    low_stock_items: int = 0


class StockStatusReport(BaseModel):
    """Stock status report"""
    warehouses: List[dict] = []
    low_stock_alerts: List[dict] = []
    reserved_items: List[dict] = []


class ExpenseSummaryReport(BaseModel):
    """Expense summary report"""
    total: Decimal = Decimal("0")
    by_project: List[dict] = []
    by_type: List[dict] = []
    by_personnel: List[dict] = []


class RevenueSummaryReport(BaseModel):
    """Revenue summary report"""
    total: Decimal = Decimal("0")
    by_project: List[dict] = []
    by_month: List[dict] = []


class CurrencyRates(BaseModel):
    """Currency rates from TCMB"""
    last_updated: datetime
    rates: dict = {}

