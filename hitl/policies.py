from enum import Enum
from typing import Any, Optional


class RiskTier(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"
    HUMAN_REVIEW_RECOMMENDED = "HUMAN_REVIEW_RECOMMENDED"
    MANDATORY_HUMAN_APPROVAL = "MANDATORY_HUMAN_APPROVAL"


class ActionRiskPolicyEngine:
    """
    Industrial Action Risk Policy Engine.
    Evaluates proposed autonomous agent actions and enforces Human-in-the-Loop safety boundaries.
    """

    # High-consequence physical or financial action triggers
    HIGH_CONSEQUENCE_ACTIONS = {
        "emergency_shutdown",
        "trip_machine",
        "power_isolation",
        "depressurize_line",
        "reflash_firmware",
        "emergency_work_order_dispatch",
    }

    REVIEW_RECOMMENDED_ACTIONS = {
        "schedule_routine_maintenance",
        "order_spare_parts",
        "calibrate_thresholds",
        "acknowledge_alert",
    }

    AUTONOMOUS_ACTIONS = {
        "query_telemetry",
        "run_anomaly_inference",
        "generate_diagnostic_report",
        "search_knowledge_manuals",
        "log_telemetry_batch",
    }

    @classmethod
    def evaluate_action(
        cls, action_type: str, details: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Classifies an action into safety risk tiers.
        """
        action_clean = action_type.strip().lower()
        details = details or {}
        risk_factors = []

        # Check estimated downtime or financial cost factors
        est_downtime = details.get("estimated_downtime_hours", 0)
        est_cost = details.get("estimated_cost_usd", 0)
        priority = details.get("priority", "").upper()

        if est_downtime >= 2.0:
            risk_factors.append(f"Estimated downtime of {est_downtime}h exceeds 2.0h safety threshold")
        if est_cost >= 1000:
            risk_factors.append(f"Estimated cost of ${est_cost} exceeds $1,000 threshold")
        if "EMERGENCY" in priority:
            risk_factors.append("Emergency priority intervention requires certified supervisor sign-off")

        # Determine Tier
        if action_clean in cls.HIGH_CONSEQUENCE_ACTIONS or len(risk_factors) > 0:
            tier = RiskTier.MANDATORY_HUMAN_APPROVAL
            requires_approval = True
        elif action_clean in cls.REVIEW_RECOMMENDED_ACTIONS:
            tier = RiskTier.HUMAN_REVIEW_RECOMMENDED
            requires_approval = False
        else:
            tier = RiskTier.AUTONOMOUS
            requires_approval = False

        return {
            "action_type": action_type,
            "risk_tier": tier.value,
            "requires_approval": requires_approval,
            "risk_factors": risk_factors,
        }
