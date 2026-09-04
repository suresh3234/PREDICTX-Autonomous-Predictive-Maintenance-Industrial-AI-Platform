from fastapi.testclient import TestClient

from apps.api.app.main import app
from hitl.approval_gate import ApprovalGateManager
from hitl.audit_trail import ImmutableAuditTrail
from hitl.policies import ActionRiskPolicyEngine, RiskTier


def test_action_risk_policy_evaluation():
    # 1. High consequence emergency action
    res_high = ActionRiskPolicyEngine.evaluate_action(action_type="emergency_shutdown", details={})
    assert res_high["risk_tier"] == RiskTier.MANDATORY_HUMAN_APPROVAL.value
    assert res_high["requires_approval"] is True

    # 2. Financial / downtime threshold escalation
    res_downtime = ActionRiskPolicyEngine.evaluate_action(
        action_type="replace_bearing", details={"estimated_downtime_hours": 3.5}
    )
    assert res_downtime["risk_tier"] == RiskTier.MANDATORY_HUMAN_APPROVAL.value
    assert res_downtime["requires_approval"] is True
    assert len(res_downtime["risk_factors"]) >= 1

    # 3. Autonomous telemetry query
    res_auto = ActionRiskPolicyEngine.evaluate_action(action_type="query_telemetry")
    assert res_auto["risk_tier"] == RiskTier.AUTONOMOUS.value
    assert res_auto["requires_approval"] is False


def test_approval_gate_lifecycle():
    gate = ApprovalGateManager(default_timeout_minutes=10)
    callback_executed = {"done": False}

    def on_approved(payload):
        callback_executed["done"] = True
        return {"executed_action": payload.get("action")}

    req = gate.request_approval(
        action_type="emergency_trip",
        machine_id="M1000",
        justification="Vibration exceeded 4.5 mm/s limit",
        action_payload={"action": "TRIP_MAIN_BREAKER"},
        on_approved_callback=on_approved,
    )

    req_id = req["request_id"]
    assert req["status"] == "PENDING"
    assert len(gate.list_pending_requests()) == 1

    # Approve request
    appr_res = gate.approve_request(
        request_id=req_id, approver_id="TECH_ALICE_404", notes="Verified bearing smoke."
    )
    assert appr_res["status"] == "APPROVED"
    assert callback_executed["done"] is True
    assert len(gate.list_pending_requests()) == 0


def test_approval_gate_rejection():
    gate = ApprovalGateManager()
    req = gate.request_approval(
        action_type="depressurize_line",
        machine_id="M1001",
        justification="Testing valve",
    )

    req_id = req["request_id"]
    rej_res = gate.reject_request(
        request_id=req_id, rejecter_id="SUPERVISOR_BOB", rejection_reason="Shift not clear."
    )
    assert rej_res["status"] == "REJECTED"

    req_state = gate.get_request(req_id)
    assert req_state["status"] == "REJECTED"
    assert req_state["decision"]["rejection_reason"] == "Shift not clear."


def test_immutable_audit_trail_integrity():
    audit = ImmutableAuditTrail()

    # Log 3 events
    b1 = audit.log_event(
        event_type="HITL_APPROVED", actor_id="TECH_ALICE", machine_id="M1000", action="SHUTDOWN"
    )
    b2 = audit.log_event(
        event_type="HITL_REJECTED", actor_id="TECH_BOB", machine_id="M1001", action="DISPATCH"
    )

    assert b2["previous_hash"] == b1["hash"]
    assert audit.verify_chain_integrity() is True

    # Test tampering detection
    audit.chain[1]["action"] = "TAMPERED_ACTION_OVERRIDE"
    assert audit.verify_chain_integrity() is False


def test_hitl_api_endpoints():
    client = TestClient(app)

    # 1. Policy evaluation endpoint
    eval_resp = client.post(
        "/api/v1/hitl/evaluate",
        json={"action_type": "emergency_shutdown", "machine_id": "M1000", "details": {}},
    )
    assert eval_resp.status_code == 200
    assert eval_resp.json()["requires_approval"] is True

    # 2. Audit endpoint
    audit_resp = client.get("/api/v1/hitl/audit")
    assert audit_resp.status_code == 200
    assert audit_resp.json()["chain_integrity_verified"] is True
