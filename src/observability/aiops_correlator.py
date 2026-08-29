import time
import uuid
from typing import Any, Optional


class AIOpsIncidentCorrelator:
    """
    AIOps Automated Incident Correlator.
    Deduplicates concurrent equipment alarms, groups related sensor deviations within
    common plant zones, and isolates cascade failure root causes.
    """

    def __init__(self, time_window_seconds: float = 300.0):
        self.time_window_seconds = time_window_seconds
        self.recent_alerts: list[dict[str, Any]] = []

    def ingest_alert(self, machine_id: str, severity: str, sensor: str, message: str, zone: str = "Zone-1") -> dict[str, Any]:
        """
        Ingests and correlates an incoming telemetry alert.
        """
        now = time.time()
        # Evict outdated alerts outside the sliding window
        self.recent_alerts = [a for a in self.recent_alerts if (now - a["timestamp"]) <= self.time_window_seconds]

        alert = {
            "alert_id": f"ALT-{uuid.uuid4().hex[:6].upper()}",
            "machine_id": machine_id,
            "severity": severity.upper(),
            "sensor": sensor,
            "message": message,
            "zone": zone,
            "timestamp": now,
        }
        self.recent_alerts.append(alert)

        # Check for correlated incident clustering
        correlated = self.correlate_zone(zone)
        return {
            "alert": alert,
            "active_window_alerts": len(self.recent_alerts),
            "correlation_cluster": correlated,
        }

    def correlate_zone(self, zone: str) -> dict[str, Any]:
        """
        Clusters alerts originating within the same operational plant zone.
        """
        zone_alerts = [a for a in self.recent_alerts if a["zone"] == zone]
        machines = list(set(a["machine_id"] for a in zone_alerts))
        critical_count = sum(1 for a in zone_alerts if a["severity"] == "CRITICAL")

        is_cascade = len(machines) >= 2 and critical_count >= 1

        if is_cascade:
            cluster_type = "PLANT_ZONE_CASCADE_EVENT"
            recommendation = f"Zone '{zone}' exhibits multi-machine cascade failure across {len(machines)} units. Inspect main power bus and coolant manifold."
        elif len(zone_alerts) > 1:
            cluster_type = "MULTI_SENSOR_ANOMALY"
            recommendation = f"Multiple sensor deviations detected in zone '{zone}'."
        else:
            cluster_type = "ISOLATED_INCIDENT"
            recommendation = "Isolated equipment alert. Standard SOP workflow assigned."

        return {
            "cluster_type": cluster_type,
            "zone": zone,
            "involved_machines": machines,
            "total_alerts": len(zone_alerts),
            "critical_count": critical_count,
            "recommendation": recommendation,
        }
