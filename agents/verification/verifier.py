import logging
from typing import Any

logger = logging.getLogger("PredictX.Agent.Verifier")


class VerificationAgent:
    """
    Safety & Operational Verification Agent.
    Validates that proposed maintenance procedures comply with Lock-Out / Tag-Out (LOTO)
    safety standards, PPE requirements, and post-repair restart protocols.
    """

    def verify_plan(self, work_order: dict[str, Any], rca_report: dict[str, Any]) -> dict[str, Any]:
        """
        Conducts safety audit and compliance review on the maintenance plan.
        """
        action_steps = work_order.get("action_steps", [])
        steps_text = " ".join(action_steps).lower()

        # 1. Check LOTO Compliance
        has_loto = "loto" in steps_text or "lock-out" in steps_text or "isolate" in steps_text or "power down" in steps_text

        # 2. Check Post-Maintenance Validation Step
        has_validation = "validate" in steps_text or "test run" in steps_text or "confirm" in steps_text or "verify" in steps_text

        # 3. Determine Required PPE
        subsystem = rca_report.get("target_subsystem", "").lower()
        ppe_list = ["ANSI Z87.1 Safety Glasses", "Steel-Toe Safety Boots"]

        if "bearing" in subsystem or "rotating" in subsystem:
            ppe_list.extend(["Cut-Resistant Mechanics Gloves", "Hearing Protection (NRR 25dB)"])
        elif "thermal" in subsystem or "cooling" in subsystem:
            ppe_list.extend(["Thermal Heat-Resistant Gloves", "Face Shield"])
        elif "hydraulic" in subsystem:
            ppe_list.extend(["Nitrile Chemical/Oil Resistant Gloves", "Full Splash Apron"])
        elif "electrical" in subsystem:
            ppe_list.extend(["NFPA 70E Arc-Flash Level 2 Suit", "Class 0 (1000V) Insulated Gloves"])

        # Determine Safety Clearance
        if has_loto and has_validation:
            clearance = "APPROVED (Full Safety Compliance)"
            is_approved = True
        elif has_loto:
            clearance = "CONDITIONAL (Requires Post-Maintenance Test Step)"
            is_approved = True
        else:
            clearance = "REJECTED (Missing Mandatory LOTO Power Isolation)"
            is_approved = False

        verification_report = {
            "agent": "VerificationAgent",
            "safety_clearance": clearance,
            "is_approved": is_approved,
            "loto_protocol_verified": has_loto,
            "post_repair_validation_verified": has_validation,
            "mandatory_ppe": ppe_list,
            "safety_warnings": [
                "Ensure all residual kinetic and thermal energy is completely dissipated before disassembling.",
                "Verify zero-voltage state with calibrated test leads prior to physical contact.",
            ],
        }

        logger.info(f"Verification Agent clearance status: {clearance}")
        return verification_report
