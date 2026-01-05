"""
Authentication Dependencies
JWT token validation and current user extraction
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models import User, Role
from app.utils.security import decode_access_token

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı hesabı devre dışı"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for get_current_user)"""
    return current_user


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(["admin"]))):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Load role
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        
        if role is None or role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetkiniz yok. Gerekli rol: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


def require_permission(module: str, action: str):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @router.post("/invoices")
        async def create_invoice(user: User = Depends(require_permission("invoices", "write"))):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Load role with permissions
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol bulunamadı"
            )
        
        permissions = role.permissions or {}
        
        # Check if user has "all" permission (admin)
        if "all" in permissions:
            if action in permissions["all"]:
                return current_user
        
        # Check specific module permission
        if module in permissions:
            if action in permissions[module]:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"'{module}' modülünde '{action}' işlemi için yetkiniz yok"
        )
    
    return permission_checker


# Common role dependencies
require_admin = require_role(["admin"])
require_manager = require_role(["admin", "manager"])
require_technician = require_role(["admin", "manager", "technician"])
require_accountant = require_role(["admin", "accountant"])
