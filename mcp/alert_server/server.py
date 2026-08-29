import uuid
from datetime import datetime
from typing import Any
from mcp.base import MCPServerBase


class AlertMCPServer(MCPServerBase):
    """
    MCP Server for Industrial Incident Alerting and Operations Dispatch.
    """

    def __init__(self):
        super().__init__(name="predictx-alert-server", version="1.0.0")
        self.alerts: list[dict[str, Any]] = []
        self._register_alert_tools()

    def _register_alert_tools(self):
        @self.tool(
            name="dispatch_alert",
            description="Dispatches an incident alert to plant operations and on-call technicians."
        )
        def dispatch_alert(
            machine_id: str,
            severity: str,
            message: str,
            trigger_sensor: str = "general",
        ) -> dict[str, Any]:
            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alert = {
                "alert_id": alert_id,
                "machine_id": machine_id,
                "severity": severity.upper(),
                "trigger_sensor": trigger_sensor,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "acknowledged": False,
            }
            self.alerts.append(alert)
            return {"status": "DISPATCHED", "alert": alert}

        @self.tool(
            name="get_active_alerts",
            description="Retrieves all active unacknowledged equipment alerts."
        )
        def get_active_alerts() -> list[dict[str, Any]]:
            return [a for a in self.alerts if not a["acknowledged"]]

        @self.tool(
            name="acknowledge_alert",
            description="Acknowledges an equipment alert by alert ID."
        )
        def acknowledge_alert(alert_id: str) -> dict[str, Any]:
            for a in self.alerts:
                if a["alert_id"] == alert_id:
                    a["acknowledged"] = True
                    return {"status": "ACKNOWLEDGED", "alert_id": alert_id}
            return {"error": f"Alert '{alert_id}' not found."}
