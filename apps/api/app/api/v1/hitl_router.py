
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from hitl.approval_gate import ApprovalGateManager
from hitl.audit_trail import ImmutableAuditTrail
from hitl.policies import ActionRiskPolicyEngine
from src.security.auth import decode_access_token
from src.security.rbac import Role, has_permission

router = APIRouter(prefix="/hitl", tags=["hitl"])

# Global singleton managers
gate_manager = ApprovalGateManager(default_timeout_minutes=30)
audit_trail = ImmutableAuditTrail()


def _get_user_role_from_header(authorization: str | None) -> tuple[str, str]:
    """Helper to extract user and role from Bearer token if provided."""
    if not authorization:
        return "system", "ENGINEER"
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return "system", "ENGINEER"
    try:
        payload = decode_access_token(token)
        return payload.get("sub", "system"), payload.get("role", "VIEWER")
    except Exception:
        return "system", "ENGINEER"


class ApprovePayload(BaseModel):
    request_id: str
    approver_id: str
    notes: str | None = "Approved by certified reliability engineer."


class RejectPayload(BaseModel):
    request_id: str
    rejecter_id: str
    reason: str


class EvaluateActionPayload(BaseModel):
    action_type: str
    machine_id: str
    details: dict | None = None


@router.post("/evaluate")
def evaluate_action_policy(payload: EvaluateActionPayload):
    """Evaluates the risk tier and human approval requirement for an action."""
    return ActionRiskPolicyEngine.evaluate_action(
        action_type=payload.action_type, details=payload.details
    )


@router.get("/requests")
def list_pending_requests():
    """Lists all pending HITL safety approval requests."""
    return {"pending_requests": gate_manager.list_pending_requests()}


@router.post("/approve")
def approve_request(payload: ApprovePayload, authorization: str | None = Header(None)):
    """Submits technician approval for a pending action with RBAC validation."""
    username, role = _get_user_role_from_header(authorization)

    # Enforce minimum role ENGINEER for approval
    if not has_permission(role, Role.ENGINEER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Approval requires minimum role 'ENGINEER'. User '{username}' has role '{role}'.",
        )

    res = gate_manager.approve_request(
        request_id=payload.request_id,
        approver_id=payload.approver_id or username,
        notes=payload.notes or "",
    )
    if res.get("status") == "ERROR":
        raise HTTPException(status_code=400, detail=res.get("message"))

    # Log to immutable audit trail
    req = gate_manager.get_request(payload.request_id)
    audit_trail.log_event(
        event_type="HITL_ACTION_APPROVED",
        actor_id=payload.approver_id,
        machine_id=req.get("machine_id", "UNKNOWN") if req else "UNKNOWN",
        action=req.get("action_type", "UNKNOWN") if req else "UNKNOWN",
        details={"request_id": payload.request_id, "notes": payload.notes},
        outcome="APPROVED",
    )
    return res


@router.post("/reject")
def reject_request(payload: RejectPayload, authorization: str | None = Header(None)):
    """Rejects a proposed action with technician rationale and RBAC validation."""
    username, role = _get_user_role_from_header(authorization)

    # Enforce minimum role ENGINEER for rejection
    if not has_permission(role, Role.ENGINEER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rejection requires minimum role 'ENGINEER'. User '{username}' has role '{role}'.",
        )

    res = gate_manager.reject_request(
        request_id=payload.request_id,
        rejecter_id=payload.rejecter_id or username,
        rejection_reason=payload.reason,
    )
    if res.get("status") == "ERROR":
        raise HTTPException(status_code=400, detail=res.get("message"))

    # Log to immutable audit trail
    req = gate_manager.get_request(payload.request_id)
    audit_trail.log_event(
        event_type="HITL_ACTION_REJECTED",
        actor_id=payload.rejecter_id or username,
        machine_id=req.get("machine_id", "UNKNOWN") if req else "UNKNOWN",
        action=req.get("action_type", "UNKNOWN") if req else "UNKNOWN",
        details={"request_id": payload.request_id, "reason": payload.reason},
        outcome="REJECTED",
    )
    return res


@router.get("/audit")
def get_audit_trail(machine_id: str | None = None):
    """Retrieves the immutable audit trail and integrity verification status."""
    is_valid = audit_trail.verify_chain_integrity()
    history = audit_trail.get_history(machine_id)
    return {
        "chain_integrity_verified": is_valid,
        "total_records": len(history),
        "history": history,
    }
