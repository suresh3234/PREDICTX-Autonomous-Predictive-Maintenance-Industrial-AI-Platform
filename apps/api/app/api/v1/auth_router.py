from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.security.auth import create_access_token, hash_password, verify_password
from src.security.rbac import Role, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Demo plant users database (In production, stored in PostgreSQL with hashed passwords)
PLANT_USERS = {
    "admin": {
        "username": "admin",
        "role": Role.ADMIN.value,
        "name": "Dr. Elena Rostova",
        "title": "Principal Reliability Engineer & System Admin",
        "password_hash": hash_password("PredictX@Admin2026", salt="salt_admin_demo"),
    },
    "engineer": {
        "username": "engineer",
        "role": Role.ENGINEER.value,
        "name": "Marcus Vance",
        "title": "Senior Mechanical Diagnostics Engineer",
        "password_hash": hash_password("Engineer@2026", salt="salt_eng_demo"),
    },
    "operator": {
        "username": "operator",
        "role": Role.OPERATOR.value,
        "name": "Sarah Chen",
        "title": "Industrial Control & Telemetry Operator",
        "password_hash": hash_password("Operator@2026", salt="salt_op_demo"),
    },
    "viewer": {
        "username": "viewer",
        "role": Role.VIEWER.value,
        "name": "Alex Mercer",
        "title": "Plant Operations Auditor & Viewer",
        "password_hash": hash_password("Viewer@2026", salt="salt_viewer_demo"),
    },
}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
def login_for_access_token(payload: LoginRequest):
    """
    Authenticates user credentials and issues a signed JWT access token.
    """
    user = PLANT_USERS.get(payload.username.lower())
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user["username"],
        role=user["role"],
        extra_claims={"name": user.get("name"), "title": user.get("title")},
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
        "name": user.get("name"),
        "title": user.get("title"),
    }


@router.get("/me")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Returns the authenticated user's profile and RBAC permissions.
    """
    u_info = PLANT_USERS.get(current_user.get("sub", "").lower(), {})
    return {
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "name": current_user.get("name") or u_info.get("name", current_user.get("sub")),
        "title": current_user.get("title") or u_info.get("title", "Plant Staff"),
        "issued_at": current_user.get("iat"),
        "expires_at": current_user.get("exp"),
    }


@router.get("/roles")
def list_roles():
    """
    Returns role hierarchies and capability specifications.
    """
    return {
        "roles": [
            {
                "role": Role.VIEWER.value,
                "level": 1,
                "badge_color": "slate",
                "capabilities": [
                    "View machine fleet telemetry",
                    "Inspect operational health indicators",
                    "Browse public system metrics and readiness probes",
                ],
            },
            {
                "role": Role.OPERATOR.value,
                "level": 2,
                "badge_color": "emerald",
                "capabilities": [
                    "All Viewer permissions",
                    "Execute real-time ML inference & RUL predictions",
                    "Acknowledge active equipment anomalies",
                    "Query grounded AI Reliability Copilot",
                    "Trigger multi-agent diagnostic investigations",
                    "Execute Model Context Protocol (MCP) diagnostics",
                ],
            },
            {
                "role": Role.ENGINEER.value,
                "level": 3,
                "badge_color": "blue",
                "capabilities": [
                    "All Operator permissions",
                    "Approve / Reject Tier-2 HITL maintenance work orders",
                    "Trigger automated ML model retraining workflows",
                    "Inspect Kolmogorov-Smirnov drift metrics",
                    "Manage knowledge base documents & SOPs",
                ],
            },
            {
                "role": Role.ADMIN.value,
                "level": 4,
                "badge_color": "purple",
                "capabilities": [
                    "All Engineer permissions",
                    "Execute Tier-3 Emergency Machine Shutdown approvals",
                    "Inspect full cryptographic SHA-256 chained audit ledger",
                    "Modify system configuration, JWT secrets, and Kafka brokers",
                    "Manage user access and RBAC permissions",
                ],
            },
        ]
    }


@router.get("/presets")
def get_demo_presets():
    """
    Returns demo login accounts for fast UI switching and testing.
    """
    presets = []
    for uname, data in PLANT_USERS.items():
        presets.append({
            "username": uname,
            "role": data["role"],
            "name": data["name"],
            "title": data["title"],
        })
    return {"presets": presets}
