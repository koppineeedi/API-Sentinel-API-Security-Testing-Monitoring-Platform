from typing import List
from fastapi import Depends, HTTPException, status
from app.dependencies import get_current_user
from app.models.user import User
from app.models.enums import UserRole

# Hierarchy mapping for "at least role" checks
ROLE_HIERARCHY = {
    UserRole.ADMIN: 3,
    UserRole.SECURITY_ANALYST: 2,
    UserRole.VIEWER: 1
}

def require_roles(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

def require_minimum_role(minimum_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.get(current_user.role, 0)
        min_level = ROLE_HIERARCHY.get(minimum_role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Minimum role required: {minimum_role.value}"
            )
        return current_user
    return role_checker
