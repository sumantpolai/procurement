from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token
from app.core.logger import setup_logger

logger = setup_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """Dependency to check if user has required role"""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            logger.warning(f"User {current_user.username} with role {current_user.role} attempted unauthorized access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user


# Role-based dependencies for PR module
pr_read_access = RoleChecker([
    UserRole.STORE_STAFF,
    UserRole.STORE_MANAGER,
    UserRole.PURCHASE_STAFF,
    UserRole.PURCHASE_MANAGER
])

pr_create_update_access = RoleChecker([
    UserRole.STORE_STAFF,
    UserRole.STORE_MANAGER
])

pr_status_update_access = RoleChecker([
    UserRole.STORE_MANAGER
])


# Role-based dependencies for PO module
po_read_access = RoleChecker([
    UserRole.STORE_STAFF,
    UserRole.STORE_MANAGER,
    UserRole.PURCHASE_STAFF,
    UserRole.PURCHASE_MANAGER
])

po_create_update_access = RoleChecker([
    UserRole.PURCHASE_STAFF,
    UserRole.PURCHASE_MANAGER
])

po_status_update_access = RoleChecker([
    UserRole.PURCHASE_MANAGER
])
