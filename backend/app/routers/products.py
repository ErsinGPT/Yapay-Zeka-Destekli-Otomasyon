"""
Products Router
Handles product/stock card management and BOM operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models import Product, ProductCategory, BOMItem, WarehouseStock
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryResponse,
    BOMItemCreate, BOMItemResponse
)
from app.routers.auth import get_current_user

router = APIRouter()


# ===== CATEGORIES =====

@router.get("/categories", response_model=List[ProductCategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all product categories"""
    categories = db.query(ProductCategory).all()
    return categories


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new product category"""
    db_category = ProductCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a product category"""
    category = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori bulunamadı"
        )
    
    # Check if any products are using this category
    products_count = db.query(Product).filter(Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu kategoride {products_count} ürün bulunmaktadır. Önce ürünleri başka kategoriye taşıyın."
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Kategori silindi"}


# ===== PRODUCTS CRUD =====

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    is_bom: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get all products with stock information.
    Returns physical stock and available stock (after reservations).
    """
    query = db.query(Product)
    
    # Filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.barcode.ilike(search_term)
            )
        )
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if is_bom is not None:
        query = query.filter(Product.is_bom == is_bom)
    
    products = query.offset(skip).limit(limit).all()
    
    # Add stock information
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "barcode": product.barcode,
            "name_en": product.name_en,
            "description": product.description,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "gtip_code": product.gtip_code,
            "unit": product.unit,
            "cost": product.cost,
            "list_price": product.list_price,
            "currency": product.currency,
            "min_stock_level": product.min_stock_level,
            "is_stockable": product.is_stockable,
            "is_purchasable": product.is_purchasable,
            "is_sellable": product.is_sellable,
            "is_bom": product.is_bom,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "total_stock": Decimal("0"),
            "available_stock": Decimal("0")
        }
        
        # Calculate total stock from all warehouses
        stock_info = db.query(
            func.sum(WarehouseStock.quantity).label("total"),
            func.sum(WarehouseStock.quantity - WarehouseStock.reserved_quantity).label("available")
        ).filter(WarehouseStock.product_id == product.id).first()
        
        if stock_info:
            product_dict["total_stock"] = stock_info.total or Decimal("0")
            product_dict["available_stock"] = stock_info.available or Decimal("0")
        
        result.append(product_dict)
    
    return result


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new product/stock card"""
    # Check SKU uniqueness
    existing = db.query(Product).filter(Product.sku == product.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SKU '{product.sku}' zaten kullanılıyor"
        )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {
        **db_product.__dict__,
        "total_stock": Decimal("0"),
        "available_stock": Decimal("0")
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product with full details"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    # Calculate total stock
    stock_info = db.query(
        func.sum(WarehouseStock.quantity).label("total"),
        func.sum(WarehouseStock.quantity - WarehouseStock.reserved_quantity).label("available")
    ).filter(WarehouseStock.product_id == product.id).first()
    
    return {
        **product.__dict__,
        "total_stock": stock_info.total or Decimal("0") if stock_info else Decimal("0"),
        "available_stock": stock_info.available or Decimal("0") if stock_info else Decimal("0")
    }


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    # Check SKU uniqueness if changing
    update_data = product_update.model_dump(exclude_unset=True)
    if "sku" in update_data and update_data["sku"] != product.sku:
        existing = db.query(Product).filter(Product.sku == update_data["sku"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU '{update_data['sku']}' zaten kullanılıyor"
            )
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    # Calculate total stock
    stock_info = db.query(
        func.sum(WarehouseStock.quantity).label("total"),
        func.sum(WarehouseStock.quantity - WarehouseStock.reserved_quantity).label("available")
    ).filter(WarehouseStock.product_id == product.id).first()
    
    return {
        **product.__dict__,
        "total_stock": stock_info.total or Decimal("0") if stock_info else Decimal("0"),
        "available_stock": stock_info.available or Decimal("0") if stock_info else Decimal("0")
    }


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    force: bool = Query(False, description="Force delete even if product has stock"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete product (soft delete - sets is_active to False)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    # Check if product has stock
    total_stock = db.query(func.sum(WarehouseStock.quantity)).filter(
        WarehouseStock.product_id == product_id
    ).scalar()
    
    if total_stock and total_stock > 0:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stoku olan ürün silinemez. Zorla silmek için force=true kullanın."
            )
        # Force delete - clear stock records
        db.query(WarehouseStock).filter(WarehouseStock.product_id == product_id).delete()
    
    product.is_active = False
    db.commit()


# ===== BOM (Bill of Materials) =====

@router.get("/{product_id}/bom", response_model=List[BOMItemResponse])
async def get_product_bom(product_id: int, db: Session = Depends(get_db)):
    """
    Get BOM (Bill of Materials) for a product.
    Returns list of child components with quantities.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    bom_items = db.query(BOMItem).filter(BOMItem.parent_product_id == product_id).all()
    
    result = []
    for item in bom_items:
        child_product = db.query(Product).filter(Product.id == item.child_product_id).first()
        result.append({
            "id": item.id,
            "parent_product_id": item.parent_product_id,
            "child_product_id": item.child_product_id,
            "quantity": item.quantity,
            "notes": item.notes,
            "child_product_name": child_product.name if child_product else None,
            "child_product_sku": child_product.sku if child_product else None
        })
    
    return result


@router.post("/{product_id}/bom", response_model=List[BOMItemResponse])
async def update_product_bom(
    product_id: int,
    bom_items: List[BOMItemCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create or update BOM for a product.
    Used for defining panel components (PLC, relays, etc.)
    Replaces existing BOM completely.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    # Mark product as BOM
    product.is_bom = True
    
    # Delete existing BOM items
    db.query(BOMItem).filter(BOMItem.parent_product_id == product_id).delete()
    
    # Create new BOM items
    new_items = []
    for item_data in bom_items:
        # Verify child product exists
        child = db.query(Product).filter(Product.id == item_data.child_product_id).first()
        if not child:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bileşen ürün ID {item_data.child_product_id} bulunamadı"
            )
        
        bom_item = BOMItem(
            parent_product_id=product_id,
            **item_data.model_dump()
        )
        db.add(bom_item)
        new_items.append(bom_item)
    
    db.commit()
    
    # Return with product info
    result = []
    for item in new_items:
        db.refresh(item)
        child_product = db.query(Product).filter(Product.id == item.child_product_id).first()
        result.append({
            "id": item.id,
            "parent_product_id": item.parent_product_id,
            "child_product_id": item.child_product_id,
            "quantity": item.quantity,
            "notes": item.notes,
            "child_product_name": child_product.name if child_product else None,
            "child_product_sku": child_product.sku if child_product else None
        })
    
    return result


@router.get("/{product_id}/barcode")
async def generate_barcode(product_id: int, db: Session = Depends(get_db)):
    """
    Generate barcode/QR code for product.
    Returns barcode URL.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    # TODO: Implement actual barcode generation with python-barcode
    barcode_value = product.barcode or product.sku
    
    return {
        "product_id": product_id,
        "sku": product.sku,
        "barcode": barcode_value,
        "barcode_url": f"/uploads/barcodes/{product_id}.png"
    }


@router.get("/{product_id}/stock-check")
async def check_bom_stock(product_id: int, db: Session = Depends(get_db)):
    """
    Check if all BOM components are available in stock.
    Returns availability status for each component.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ürün bulunamadı"
        )
    
    if not product.is_bom:
        return {
            "product_id": product_id,
            "is_bom": False,
            "can_produce": True,
            "missing_components": []
        }
    
    bom_items = db.query(BOMItem).filter(BOMItem.parent_product_id == product_id).all()
    
    missing_components = []
    can_produce = True
    
    for item in bom_items:
        # Get available stock for component
        stock_info = db.query(
            func.sum(WarehouseStock.quantity - WarehouseStock.reserved_quantity).label("available")
        ).filter(WarehouseStock.product_id == item.child_product_id).first()
        
        available = stock_info.available or Decimal("0") if stock_info else Decimal("0")
        
        if available < item.quantity:
            can_produce = False
            child_product = db.query(Product).filter(Product.id == item.child_product_id).first()
            missing_components.append({
                "product_id": item.child_product_id,
                "product_name": child_product.name if child_product else "Bilinmeyen",
                "required": float(item.quantity),
                "available": float(available),
                "shortage": float(item.quantity - available)
            })
    
    return {
        "product_id": product_id,
        "is_bom": True,
        "can_produce": can_produce,
        "missing_components": missing_components
    }
