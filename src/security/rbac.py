from enum import Enum
from typing import Any, Optional
from fastapi import Header, HTTPException, status
from src.security.auth import decode_access_token


class Role(str, Enum):
    VIEWER = "VIEWER"
    OPERATOR = "OPERATOR"
    ENGINEER = "ENGINEER"
    ADMIN = "ADMIN"


ROLE_HIERARCHY = {
    Role.VIEWER.value: 1,
    Role.OPERATOR.value: 2,
    Role.ENGINEER.value: 3,
    Role.ADMIN.value: 4,
}


def has_permission(user_role: str, min_required_role: Role) -> bool:
    """
    Checks if user's role rank meets or exceeds the required rank.
    """
    u_level = ROLE_HIERARCHY.get(user_role.upper(), 0)
    req_level = ROLE_HIERARCHY.get(min_required_role.value, 99)
    return u_level >= req_level


def get_current_user(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the JWT bearer token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(min_role: Role):
    """
    FastAPI dependency factory enforcing minimum RBAC role rank.
    """
    def role_checker(user: dict[str, Any] = None):
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User identity could not be verified.",
            )
        user_role = user.get("role", "VIEWER")
        if not has_permission(user_role, min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires minimum role '{min_role.value}'. User has '{user_role}'.",
            )
        return user
    return role_checker
