from pathlib import Path

from agents.investigator.investigator import InvestigatorAgent
from agents.maintenance.planner import MaintenancePlannerAgent
from agents.root_cause.rca_agent import RootCauseAgent
from agents.supervisor.supervisor import SupervisorAgent
from agents.verification.verifier import VerificationAgent
from rag.engine import AdvancedRAGEngine


def test_investigator_agent_anomaly_detection():
    investigator = InvestigatorAgent()

    anomalous_telemetry = {
        "machine_id": "M1000",
        "vibration": 4.2,  # > 3.5 limit
        "temperature": 78.0,  # > 75 limit
        "pressure": 100.0,
        "current": 11.0,
    }

    report = investigator.investigate(anomalous_telemetry)
    assert report["agent"] == "InvestigatorAgent"
    assert report["audit_summary"]["is_anomalous"] is True
    assert report["audit_summary"]["breach_count"] == 2
    assert report["ml_diagnostics"]["anomaly_severity"] == "CRITICAL"


def test_root_cause_agent_diagnosis():
    rca = RootCauseAgent()

    inv_report = {
        "machine_id": "M1000",
        "audit_summary": {
            "is_anomalous": True,
            "breaches": [
                {"sensor": "vibration", "value": 4.2, "threshold": 3.5, "severity": "CRITICAL"}
            ],
        },
    }

    diag = rca.diagnose_root_cause(inv_report)
    assert diag["agent"] == "RootCauseAgent"
    assert "Bearing" in diag["primary_failure_mode"]
    assert diag["triggering_sensor"] == "vibration"
    assert diag["confidence"] > 0.85


def test_maintenance_planner_agent():
    planner = MaintenancePlannerAgent()

    rca_report = {
        "primary_failure_mode": "Bearing Wear / Shaft Misalignment",
        "target_subsystem": "Rotating Drive / Bearings",
    }

    work_order = planner.generate_plan(rca_report)
    assert work_order["agent"] == "MaintenancePlannerAgent"
    assert "Bearing" in work_order["work_order_title"]
    assert len(work_order["required_parts"]) >= 1
    assert len(work_order["action_steps"]) >= 4
    assert work_order["estimated_downtime_hours"] > 0


def test_verification_agent_safety_audit():
    verifier = VerificationAgent()

    work_order = {
        "action_steps": [
            "1. Isolate machine power and apply Lock-Out / Tag-Out (LOTO).",
            "2. Replace defective ball bearings.",
            "3. Perform vibration test run to validate nominal status.",
        ]
    }
    rca_report = {"target_subsystem": "Rotating Drive / Bearings"}

    safe_report = verifier.verify_plan(work_order, rca_report)
    assert safe_report["agent"] == "VerificationAgent"
    assert safe_report["is_approved"] is True
    assert safe_report["loto_protocol_verified"] is True
    assert safe_report["post_repair_validation_verified"] is True
    assert len(safe_report["mandatory_ppe"]) >= 2


def test_supervisor_agent_end_to_end():
    root = Path(__file__).resolve().parents[2]
    manuals_path = root / "data" / "knowledge" / "manuals.json"

    rag_engine = AdvancedRAGEngine()
    rag_engine.index_file_or_directory(manuals_path)

    supervisor = SupervisorAgent(rag_engine=rag_engine)

    telemetry = {
        "machine_id": "M1000",
        "vibration": 3.9,
        "temperature": 68.0,
        "pressure": 95.0,
        "current": 11.5,
    }

    master_report = supervisor.run_investigation(telemetry)

    assert "INC-M1000" in master_report["incident_id"]
    assert master_report["overall_status"] == "CRITICAL ACTION REQUIRED"
    assert "investigation" in master_report
    assert "root_cause_analysis" in master_report
    assert "maintenance_work_order" in master_report
    assert "safety_verification" in master_report

    # Test markdown report rendering
    md = supervisor.format_markdown_report(master_report)
    assert "# 🚨 Incident Diagnostic" in md
    assert "Investigator Agent" in md
    assert "RCA Agent" in md
    assert "Maintenance Planner Agent" in md
    assert "Verifier Agent" in md
