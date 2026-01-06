"""
Settings Router
Handles application settings and configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import json
import os

from app.database import get_db
from app.schemas import AppSettings, CompanySettings, InvoiceNumberingSettings
from app.routers.auth import get_current_user
from app.config import settings as app_config

router = APIRouter()

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(app_config.DATABASE_URL.replace("sqlite:///", "")), "app_settings.json")


def load_settings() -> dict:
    """Load settings from file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    
    # Return defaults
    return {
        "company": {
            "company_name": "Otomasyon A.Ş.",
            "company_name_en": "Otomasyon Inc.",
            "tax_office": "",
            "tax_id": "",
            "address": "",
            "phone": "",
            "email": "",
            "website": "",
            "logo_url": ""
        },
        "invoice_numbering": {
            "prefix": "FTR",
            "year_format": "%Y",
            "separator": "-",
            "padding": 6,
            "next_number": 1
        },
        "default_currency": "TRY",
        "default_vat_rate": "20.00"
    }


def save_settings(data: dict) -> bool:
    """Save settings to file"""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


@router.get("/", response_model=AppSettings)
async def get_settings(
    current_user = Depends(get_current_user)
):
    """Get all application settings"""
    data = load_settings()
    return AppSettings(**data)


@router.put("/")
async def update_settings(
    settings_update: AppSettings,
    current_user = Depends(get_current_user)
):
    """Update all application settings"""
    # Check admin permission
    user_role = current_user.role.name if current_user.role else ""
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Ayarları güncelleme yetkiniz yok")
    
    data = settings_update.model_dump()
    # Convert Decimal to string for JSON serialization
    data["default_vat_rate"] = str(data["default_vat_rate"])
    
    if save_settings(data):
        return {"message": "Ayarlar güncellendi"}
    else:
        raise HTTPException(status_code=500, detail="Ayarlar kaydedilemedi")


@router.get("/company", response_model=CompanySettings)
async def get_company_settings(
    current_user = Depends(get_current_user)
):
    """Get company settings"""
    data = load_settings()
    return CompanySettings(**data.get("company", {}))


@router.put("/company")
async def update_company_settings(
    company: CompanySettings,
    current_user = Depends(get_current_user)
):
    """Update company settings"""
    # Check admin permission
    user_role = current_user.role.name if current_user.role else ""
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Şirket ayarlarını güncelleme yetkiniz yok")
    
    data = load_settings()
    data["company"] = company.model_dump()
    
    if save_settings(data):
        return {"message": "Şirket ayarları güncellendi"}
    else:
        raise HTTPException(status_code=500, detail="Ayarlar kaydedilemedi")


@router.get("/invoice-numbering", response_model=InvoiceNumberingSettings)
async def get_invoice_numbering(
    current_user = Depends(get_current_user)
):
    """Get invoice numbering settings"""
    data = load_settings()
    return InvoiceNumberingSettings(**data.get("invoice_numbering", {}))


@router.put("/invoice-numbering")
async def update_invoice_numbering(
    numbering: InvoiceNumberingSettings,
    current_user = Depends(get_current_user)
):
    """Update invoice numbering settings"""
    # Check admin permission
    user_role = current_user.role.name if current_user.role else ""
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Fatura numaralama ayarlarını güncelleme yetkiniz yok")
    
    data = load_settings()
    data["invoice_numbering"] = numbering.model_dump()
    
    if save_settings(data):
        return {"message": "Fatura numaralama ayarları güncellendi"}
    else:
        raise HTTPException(status_code=500, detail="Ayarlar kaydedilemedi")


@router.get("/currencies")
async def get_available_currencies():
    """Get list of available currencies"""
    return {
        "currencies": [
            {"code": "TRY", "name": "Türk Lirası", "symbol": "₺"},
            {"code": "USD", "name": "ABD Doları", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "İngiliz Sterlini", "symbol": "£"}
        ],
        "default": "TRY"
    }


@router.get("/expense-types")
async def get_expense_types():
    """Get available expense types"""
    return {
        "types": [
            {"code": "TRAVEL", "name": "Seyahat"},
            {"code": "ACCOMMODATION", "name": "Konaklama"},
            {"code": "FOOD", "name": "Yemek"},
            {"code": "TRANSPORT", "name": "Ulaşım"},
            {"code": "MATERIAL", "name": "Malzeme"},
            {"code": "OTHER", "name": "Diğer"}
        ]
    }


@router.get("/warehouse-types")
async def get_warehouse_types():
    """Get available warehouse types"""
    return {
        "types": [
            {"code": "PHYSICAL", "name": "Fiziksel Depo"},
            {"code": "VIRTUAL", "name": "Araç Deposu"}
        ]
    }


@router.get("/project-statuses")
async def get_project_statuses():
    """Get available project statuses with descriptions"""
    return {
        "statuses": [
            {"code": "WON", "name": "Kazanıldı", "description": "Proje kazanıldı, başlamayı bekliyor"},
            {"code": "ENGINEERING", "name": "Mühendislik", "description": "Mühendislik tasarım aşaması"},
            {"code": "PROCUREMENT", "name": "Satın Alma", "description": "Malzeme tedarik aşaması"},
            {"code": "MANUFACTURING", "name": "İmalat", "description": "Üretim aşaması"},
            {"code": "TESTING", "name": "Test", "description": "Test ve kalite kontrol"},
            {"code": "INSTALLATION", "name": "Kurulum", "description": "Saha kurulum aşaması"},
            {"code": "COMMISSIONING", "name": "Devreye Alma", "description": "Sistem devreye alma"},
            {"code": "TRAINING", "name": "Eğitim", "description": "Kullanıcı eğitimi"},
            {"code": "COMPLETED", "name": "Tamamlandı", "description": "Proje tamamlandı"},
            {"code": "INVOICED", "name": "Faturalandı", "description": "Fatura kesildi"}
        ]
    }


@router.get("/invoice-statuses")
async def get_invoice_statuses():
    """Get available invoice statuses"""
    return {
        "statuses": [
            {"code": "DRAFT", "name": "Taslak"},
            {"code": "SENT", "name": "Gönderildi"},
            {"code": "PAID", "name": "Ödendi"},
            {"code": "CANCELLED", "name": "İptal"}
        ]
    }
