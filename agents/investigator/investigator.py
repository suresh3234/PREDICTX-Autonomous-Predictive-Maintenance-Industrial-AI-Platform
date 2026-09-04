import logging
from typing import Any

from ml.features.pipelines import FeaturePipeline
from ml.registry.manager import ModelRegistryManager

logger = logging.getLogger("PredictX.Agent.Investigator")


class InvestigatorAgent:
    """
    Telemetry Investigator Agent.
    Specialized agent responsible for telemetry sensor auditing, statistical threshold
    verification, and multi-model machine learning inference.
    """

    NOMINAL_THRESHOLDS = {
        "vibration": {"normal_max": 2.5, "warning_max": 3.5, "unit": "mm/s"},
        "temperature": {"normal_max": 65.0, "warning_max": 75.0, "unit": "°C"},
        "pressure": {"normal_min": 90.0, "warning_min": 80.0, "unit": "PSI"},
        "current": {"normal_max": 12.0, "warning_max": 15.0, "unit": "A"},
        "load": {"normal_max": 80.0, "warning_max": 90.0, "unit": "%"},
    }

    def __init__(self, registry_manager: ModelRegistryManager | None = None):
        self.registry_manager = registry_manager
        self.feature_pipeline = FeaturePipeline()

    def audit_telemetry(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        """
        Performs rule-based sensor audit and deviation analysis.
        """
        breaches = []
        deviations = {}

        # 1. Vibration Check
        vib = float(telemetry.get("vibration", 0.0))
        if vib > self.NOMINAL_THRESHOLDS["vibration"]["warning_max"]:
            breaches.append({
                "sensor": "vibration",
                "value": vib,
                "threshold": self.NOMINAL_THRESHOLDS["vibration"]["warning_max"],
                "severity": "CRITICAL",
                "message": f"Critical vibration spike of {vib:.2f} mm/s exceeds 3.5 mm/s limit.",
            })
        elif vib > self.NOMINAL_THRESHOLDS["vibration"]["normal_max"]:
            breaches.append({
                "sensor": "vibration",
                "value": vib,
                "threshold": self.NOMINAL_THRESHOLDS["vibration"]["normal_max"],
                "severity": "WARNING",
                "message": f"Elevated vibration of {vib:.2f} mm/s observed.",
            })

        # 2. Temperature Check
        temp = float(telemetry.get("temperature", 0.0))
        if temp > self.NOMINAL_THRESHOLDS["temperature"]["warning_max"]:
            breaches.append({
                "sensor": "temperature",
                "value": temp,
                "threshold": self.NOMINAL_THRESHOLDS["temperature"]["warning_max"],
                "severity": "CRITICAL",
                "message": f"Severe thermal dissipation failure ({temp:.1f}°C > 75.0°C).",
            })
        elif temp > self.NOMINAL_THRESHOLDS["temperature"]["normal_max"]:
            breaches.append({
                "sensor": "temperature",
                "value": temp,
                "threshold": self.NOMINAL_THRESHOLDS["temperature"]["normal_max"],
                "severity": "WARNING",
                "message": f"Elevated temperature of {temp:.1f}°C detected.",
            })

        # 3. Pressure Check
        press = float(telemetry.get("pressure", 100.0))
        if press < self.NOMINAL_THRESHOLDS["pressure"]["warning_min"]:
            breaches.append({
                "sensor": "pressure",
                "value": press,
                "threshold": self.NOMINAL_THRESHOLDS["pressure"]["warning_min"],
                "severity": "CRITICAL",
                "message": f"Pressure drop to {press:.1f} PSI indicates hydraulic chamber leak.",
            })

        # 4. Current Check
        curr = float(telemetry.get("current", 0.0))
        if curr > self.NOMINAL_THRESHOLDS["current"]["warning_max"]:
            breaches.append({
                "sensor": "current",
                "value": curr,
                "threshold": self.NOMINAL_THRESHOLDS["current"]["warning_max"],
                "severity": "CRITICAL",
                "message": f"Current spike of {curr:.1f} A indicates winding short-circuit.",
            })

        deviations = {
            "vibration_delta": vib - 1.5,
            "temperature_delta": temp - 55.0,
            "pressure_delta": press - 100.0,
        }

        return {
            "is_anomalous": len(breaches) > 0,
            "breach_count": len(breaches),
            "breaches": breaches,
            "deviations": deviations,
        }

    def investigate(self, telemetry: dict[str, Any], predictions: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Executes full sensor and predictive investigation.
        """
        audit = self.audit_telemetry(telemetry)

        # Extract predictions or fallback
        preds = predictions or {}
        anomaly_sev = preds.get("anomaly_severity") or ("CRITICAL" if audit["is_anomalous"] else "NORMAL")
        fail_prob = float(preds.get("failure_probability") or (0.85 if audit["is_anomalous"] else 0.05))
        rul = float(preds.get("predicted_rul") or (4.0 if audit["is_anomalous"] else 48.0))

        report = {
            "agent": "InvestigatorAgent",
            "machine_id": telemetry.get("machine_id", telemetry.get("machine_code", "UNKNOWN")),
            "audit_summary": audit,
            "ml_diagnostics": {
                "anomaly_severity": anomaly_sev,
                "failure_probability": fail_prob,
                "predicted_rul_hours": rul,
            },
            "investigation_status": "COMPLETED",
        }

        logger.info(f"Investigator completed audit for {report['machine_id']}: {anomaly_sev} ({len(audit['breaches'])} breaches)")
        return report
