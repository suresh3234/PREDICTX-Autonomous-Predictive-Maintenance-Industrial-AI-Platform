import logging
import uuid
from datetime import datetime
from typing import Any

from agents.investigator.investigator import InvestigatorAgent
from agents.maintenance.planner import MaintenancePlannerAgent
from agents.root_cause.rca_agent import RootCauseAgent
from agents.verification.verifier import VerificationAgent
from ml.registry.manager import ModelRegistryManager
from rag.engine import AdvancedRAGEngine

logger = logging.getLogger("PredictX.Agent.Supervisor")


class SupervisorAgent:
    """
    Multi-Agent Supervisor Orchestrator.
    Manages end-to-end incident investigation workflows across specialized sub-agents:
    1. InvestigatorAgent (Telemetry Audit & ML Inference)
    2. RootCauseAgent (Failure Mode Physics & RAG Context)
    3. MaintenancePlannerAgent (SOP, Tooling, Parts, Downtime)
    4. VerificationAgent (Safety, LOTO, PPE Clearance)
    """

    def __init__(
        self,
        investigator: InvestigatorAgent | None = None,
        root_cause_agent: RootCauseAgent | None = None,
        maintenance_planner: MaintenancePlannerAgent | None = None,
        verifier: VerificationAgent | None = None,
        rag_engine: AdvancedRAGEngine | None = None,
        registry_manager: ModelRegistryManager | None = None,
    ):
        self.investigator = investigator or InvestigatorAgent(registry_manager=registry_manager)
        self.root_cause_agent = root_cause_agent or RootCauseAgent(rag_engine=rag_engine)
        self.maintenance_planner = maintenance_planner or MaintenancePlannerAgent()
        self.verifier = verifier or VerificationAgent()

    def run_investigation(
        self, telemetry: dict[str, Any], predictions: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinates full multi-agent collaborative investigation.
        """
        machine_id = telemetry.get("machine_id", telemetry.get("machine_code", "M1000"))
        incident_id = f"INC-{machine_id}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"Supervisor starting investigation for incident {incident_id} ({machine_id})...")

        # Step 1: Telemetry Investigation
        inv_report = self.investigator.investigate(telemetry, predictions)

        # Step 2: Root Cause Diagnostics
        rca_report = self.root_cause_agent.diagnose_root_cause(inv_report)

        # Step 3: Maintenance SOP & Work Order Planning
        work_order = self.maintenance_planner.generate_plan(rca_report)

        # Step 4: Safety Verification & Compliance Audit
        safety_report = self.verifier.verify_plan(work_order, rca_report)

        # Step 5: Master Report Synthesis
        is_anomalous = inv_report["audit_summary"]["is_anomalous"]
        if is_anomalous:
            summary = (
                f"Machine {machine_id} exhibits critical operational anomalies "
                f"triggered by {rca_report['triggering_sensor']} at {rca_report['trigger_value']}. "
                f"Root cause diagnosed as '{rca_report['primary_failure_mode']}'. "
                f"Work order '{work_order['work_order_title']}' has been safety-cleared."
            )
        else:
            summary = f"Machine {machine_id} is operating within nominal operational thresholds."

        master_report = {
            "incident_id": incident_id,
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_status": "CRITICAL ACTION REQUIRED" if is_anomalous else "NOMINAL",
            "executive_summary": summary,
            "investigation": inv_report,
            "root_cause_analysis": rca_report,
            "maintenance_work_order": work_order,
            "safety_verification": safety_report,
        }

        logger.info(f"Supervisor investigation complete for {incident_id}: {master_report['overall_status']}")
        return master_report

    def format_markdown_report(self, report: dict[str, Any]) -> str:
        """
        Formats the master incident report into a human-readable engineering work order.
        """
        inv = report["investigation"]
        rca = report["root_cause_analysis"]
        wo = report["maintenance_work_order"]
        safe = report["safety_verification"]

        md = f"""# 🚨 Incident Diagnostic & Work Order: {report['incident_id']}
**Machine ID:** `{report['machine_id']}` | **Status:** `{report['overall_status']}` | **Timestamp:** `{report['timestamp']}`

---

## 📋 Executive Summary
{report['executive_summary']}

---

## 🔬 1. Sensor Telemetry Audit (Investigator Agent)
* **Anomaly Severity:** `{inv['ml_diagnostics']['anomaly_severity']}`
* **Failure Probability:** `{inv['ml_diagnostics']['failure_probability']*100:.1f}%`
* **Remaining Useful Life:** `{inv['ml_diagnostics']['predicted_rul_hours']:.1f} Hours`
* **Sensor Breaches:**
"""
        for b in inv["audit_summary"]["breaches"]:
            md += f"  - ⚠️ **{b['sensor'].upper()}**: `{b['value']}` (Threshold: `{b['threshold']}`) → *{b['message']}*\n"

        md += f"""
---

## 🔍 2. Root Cause Analysis (RCA Agent)
* **Diagnosed Failure Mode:** **{rca['primary_failure_mode']}** (Confidence: `{rca['confidence']*100:.0f}%`)
* **Target Subsystem:** `{rca.get('target_subsystem', 'N/A')}`
* **Hypothesis:** {rca['root_cause_hypothesis']}

---

## 🛠️ 3. Maintenance Work Order (Maintenance Planner Agent)
* **Title:** **{wo['work_order_title']}**
* **Priority:** `{wo['priority_level']}` | **Estimated Downtime:** `{wo['estimated_downtime_hours']} Hours`
* **Required Parts:**
"""
        for p in wo["required_parts"]:
            md += f"  - `{p['part_no']}`: {p['desc']} (Qty: {p['qty']})\n"

        md += "* **Action Steps:**\n"
        for step in wo["action_steps"]:
            md += f"  {step}\n"

        md += f"""
---

## 🛡️ 4. Safety Verification (Verifier Agent)
* **Safety Clearance:** **{safe['safety_clearance']}**
* **Mandatory PPE:** {', '.join(safe['mandatory_ppe'])}
"""
        return md
