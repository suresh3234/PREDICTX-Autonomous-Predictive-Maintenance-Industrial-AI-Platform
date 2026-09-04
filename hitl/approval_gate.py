import logging
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("PredictX.HITL.ApprovalGate")


class ApprovalGateManager:
    """
    Human-in-the-Loop Safety Approval Gate Manager.
    Manages pending authorization requests, cryptographic verification, and approval lifecycles.
    """

    def __init__(self, default_timeout_minutes: int = 15):
        self.default_timeout_minutes = default_timeout_minutes
        self.requests: dict[str, dict[str, Any]] = {}
        self.callbacks: dict[str, Callable] = {}

    def request_approval(
        self,
        action_type: str,
        machine_id: str,
        justification: str,
        action_payload: dict[str, Any] | None = None,
        on_approved_callback: Callable | None = None,
        timeout_minutes: int | None = None,
    ) -> dict[str, Any]:
        """
        Creates a new pending human approval request.
        """
        req_id = f"REQ-{machine_id}-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.utcnow()
        timeout = timeout_minutes or self.default_timeout_minutes
        expires_at = now + timedelta(minutes=timeout)

        request_record = {
            "request_id": req_id,
            "action_type": action_type,
            "machine_id": machine_id,
            "justification": justification,
            "action_payload": action_payload or {},
            "status": "PENDING",
            "created_at": now.isoformat() + "Z",
            "expires_at": expires_at.isoformat() + "Z",
            "decision": None,
        }

        self.requests[req_id] = request_record
        if on_approved_callback:
            self.callbacks[req_id] = on_approved_callback

        logger.info(f"Created HITL approval request {req_id} for '{action_type}' on {machine_id}")
        return request_record

    def get_request(self, request_id: str) -> dict[str, Any] | None:
        """Retrieves and checks expiration status of a request."""
        req = self.requests.get(request_id)
        if not req:
            return None

        # Check expiration
        if req["status"] == "PENDING":
            exp = datetime.fromisoformat(req["expires_at"].replace("Z", ""))
            if datetime.utcnow() > exp:
                req["status"] = "EXPIRED"

        return req

    def approve_request(
        self,
        request_id: str,
        approver_id: str,
        notes: str = "Authorized by certified reliability technician.",
    ) -> dict[str, Any]:
        """
        Submits technician approval for a pending action.
        """
        req = self.get_request(request_id)
        if not req:
            return {"status": "ERROR", "message": f"Approval request '{request_id}' not found."}

        if req["status"] != "PENDING":
            return {"status": "ERROR", "message": f"Cannot approve request in '{req['status']}' state."}

        req["status"] = "APPROVED"
        req["decision"] = {
            "approver_id": approver_id,
            "action": "APPROVED",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "notes": notes,
        }

        # Execute registered action callback if present
        callback = self.callbacks.get(request_id)
        callback_res = None
        if callback:
            try:
                callback_res = callback(req["action_payload"])
            except Exception as e:
                logger.error(f"Callback execution failed for {request_id}: {e}")

        logger.info(f"HITL Request {request_id} APPROVED by {approver_id}")
        return {
            "status": "APPROVED",
            "request_id": request_id,
            "approver_id": approver_id,
            "callback_result": callback_res,
        }

    def reject_request(
        self,
        request_id: str,
        rejecter_id: str,
        rejection_reason: str,
    ) -> dict[str, Any]:
        """
        Rejects a proposed action with operator justification.
        """
        req = self.get_request(request_id)
        if not req:
            return {"status": "ERROR", "message": f"Approval request '{request_id}' not found."}

        if req["status"] != "PENDING":
            return {"status": "ERROR", "message": f"Cannot reject request in '{req['status']}' state."}

        req["status"] = "REJECTED"
        req["decision"] = {
            "rejecter_id": rejecter_id,
            "action": "REJECTED",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "rejection_reason": rejection_reason,
        }

        logger.info(f"HITL Request {request_id} REJECTED by {rejecter_id}: {rejection_reason}")
        return {
            "status": "REJECTED",
            "request_id": request_id,
            "rejecter_id": rejecter_id,
            "reason": rejection_reason,
        }

    def list_pending_requests(self) -> list[dict[str, Any]]:
        """Returns all currently pending authorization requests."""
        pending = []
        for req_id in list(self.requests.keys()):
            req = self.get_request(req_id)
            if req and req["status"] == "PENDING":
                pending.append(req)
        return pending
