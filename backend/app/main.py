"""
Betsan CRM - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, customers, opportunities, projects, products, warehouses, stock, invoices, expenses, service_forms, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Betsan CRM başlatılıyor...")
    
    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # TODO: Start TCMB currency scheduler
    
    yield
    
    # Shutdown
    print("👋 Betsan CRM kapatılıyor...")


app = FastAPI(
    title="Betsan CRM API",
    description="Proje Odaklı CRM, Sanal Depo ve Finansal Entegrasyon Modülü",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if not exists (must be before mount)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(customers.router, prefix="/api/customers", tags=["CRM - Customers"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["CRM - Opportunities"])
app.include_router(projects.router, prefix="/api/projects", tags=["CRM - Projects"])
app.include_router(products.router, prefix="/api/products", tags=["Inventory - Products"])
app.include_router(warehouses.router, prefix="/api/warehouses", tags=["Inventory - Warehouses"])
app.include_router(stock.router, prefix="/api/stock", tags=["Inventory - Stock"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Finance - Invoices"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Finance - Expenses"])
app.include_router(service_forms.router, prefix="/api/service-forms", tags=["Operations - Service Forms"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Betsan CRM",
        "version": "1.0.0"
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Implement actual check
        "tcmb": "connected"  # TODO: Implement actual check
    }
