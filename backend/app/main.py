"""
Otomasyon CRM - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings as app_settings
from app.database import engine, Base
from app.routers import auth, users, customers, opportunities, projects, products, warehouses, stock, invoices, expenses, service_forms, delivery_notes, reports
from app.routers import settings as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Otomasyon CRM başlatılıyor...")
    
    # Create upload directory if not exists
    os.makedirs(app_settings.UPLOAD_DIR, exist_ok=True)
    
    # TODO: Start TCMB currency scheduler
    
    yield
    
    # Shutdown
    print("👋 Otomasyon CRM kapatılıyor...")


app = FastAPI(
    title="Otomasyon CRM API",
    description="Proje Odaklı CRM, Sanal Depo ve Finansal Entegrasyon Modülü",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware - Development modunda tüm originlere izin ver
# Credentials ile birlikte * kullanılamaz, bu yüzden dinamik origin ekliyoruz
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin", "")
        
        # Preflight (OPTIONS) isteği
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "600"
            return response
        
        response = await call_next(request)
        
        # Her response'a CORS headerları ekle
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

app.add_middleware(DynamicCORSMiddleware)

# Create upload directory if not exists (must be before mount)
os.makedirs(app_settings.UPLOAD_DIR, exist_ok=True)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=app_settings.UPLOAD_DIR), name="uploads")

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
app.include_router(delivery_notes.router, prefix="/api/delivery-notes", tags=["Operations - Delivery Notes"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Otomasyon CRM",
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
