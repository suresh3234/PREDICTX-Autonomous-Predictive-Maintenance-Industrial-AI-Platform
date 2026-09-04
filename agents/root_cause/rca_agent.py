import logging
from typing import Any

from rag.engine import AdvancedRAGEngine

logger = logging.getLogger("PredictX.Agent.RootCause")


class RootCauseAgent:
    """
    Root Cause Analysis (RCA) Agent.
    Correlates anomalous sensor signatures with mechanical/electrical physics failure modes
    and retrieves matching technical documentation using Advanced RAG.
    """

    FAILURE_SIGNATURES = {
        "vibration": {
            "mode": "Bearing Wear / Shaft Misalignment",
            "hypothesis": "Inner/outer raceway spalling causing high-amplitude radial vibration and acoustic noise.",
            "subsystem": "Rotating Drive / Bearings",
            "search_query": "Bearing wear vibration breakdown procedures",
        },
        "temperature": {
            "mode": "Thermal Dissipation / Cooling System Failure",
            "hypothesis": "Coolant fluid line blockage or dust clogging on radiator fins impeding heat dissipation.",
            "subsystem": "Cooling System",
            "search_query": "Overheating thermal radiator cooling fan maintenance",
        },
        "pressure": {
            "mode": "Hydraulic Chamber Seal Rupture",
            "hypothesis": "Gasket degradation or loose coupling bolts causing fluid pressure drop.",
            "subsystem": "Hydraulics",
            "search_query": "Hydraulic pressure drop fluid seal O-ring gasket repair",
        },
        "current": {
            "mode": "Electrical Stator Winding Short-Circuit",
            "hypothesis": "Insulation resistance degradation leading to high current phase imbalance.",
            "subsystem": "Electrical Motor",
            "search_query": "Electrical power winding short circuit current spikes",
        },
    }

    def __init__(self, rag_engine: AdvancedRAGEngine | None = None):
        self.rag_engine = rag_engine

    def diagnose_root_cause(self, investigator_report: dict[str, Any]) -> dict[str, Any]:
        """
        Performs RCA on investigator findings and retrieves grounded manual context.
        """
        audit = investigator_report.get("audit_summary", {})
        breaches = audit.get("breaches", [])

        if not breaches:
            return {
                "agent": "RootCauseAgent",
                "primary_failure_mode": "Healthy Operational Baseline",
                "root_cause_hypothesis": "All monitored sensor telemetry parameters remain within nominal envelopes.",
                "confidence": 0.98,
                "subsystem": "All Systems Nominal",
                "retrieved_sop_references": [],
            }

        # Select primary breach (prioritizing CRITICAL over WARNING)
        primary_breach = sorted(
            breaches,
            key=lambda b: 1 if b["severity"] == "CRITICAL" else 0,
            reverse=True,
        )[0]

        sensor = primary_breach["sensor"]
        sig = self.FAILURE_SIGNATURES.get(sensor, {
            "mode": f"Uncategorized {sensor.title()} Anomaly",
            "hypothesis": f"Sensor {sensor} exceeded threshold of {primary_breach['threshold']}.",
            "subsystem": "Unknown",
            "search_query": f"{sensor} anomaly troubleshooting manual",
        })

        # Query Advanced RAG Engine for grounded engineering manuals
        sop_docs = []
        if self.rag_engine:
            try:
                sop_docs = self.rag_engine.retrieve(query=sig["search_query"], top_k=2)
            except Exception as e:
                logger.warning(f"RAG retrieval failed during RCA: {e}")

        rca_result = {
            "agent": "RootCauseAgent",
            "primary_failure_mode": sig["mode"],
            "root_cause_hypothesis": sig["hypothesis"],
            "target_subsystem": sig["subsystem"],
            "triggering_sensor": sensor,
            "trigger_value": primary_breach["value"],
            "confidence": 0.92,
            "retrieved_sop_references": [
                {
                    "doc_id": d.get("document_id") or d.get("id"),
                    "text": d.get("text", "")[:200] + "...",
                    "score": d.get("rerank_score", d.get("score", 0.9)),
                }
                for d in sop_docs
            ],
        }

        logger.info(f"RCA diagnosed {sig['mode']} for {investigator_report.get('machine_id')}")
        return rca_result
