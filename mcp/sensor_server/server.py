from pathlib import Path
from typing import Any

import pandas as pd

from mcp.base import MCPServerBase


class SensorMCPServer(MCPServerBase):
    """
    MCP Server for Industrial IoT Sensor Telemetry Streams.
    """

    def __init__(self, data_path: str | None = None):
        super().__init__(name="predictx-sensor-server", version="1.0.0")
        root = Path(__file__).resolve().parents[2]
        self.data_path = Path(data_path) if data_path else (root / "data" / "synthetic" / "sensor_readings.csv")
        self._df = None
        self._load_data()
        self._register_sensor_tools()

    def _load_data(self):
        if self.data_path.exists():
            self._df = pd.read_csv(self.data_path)

    def _register_sensor_tools(self):
        @self.tool(
            name="get_latest_telemetry",
            description="Fetches the most recent live sensor readings (temperature, vibration, pressure, rpm, current, power) for a specified machine."
        )
        def get_latest_telemetry(machine_id: str = "M1000") -> dict[str, Any]:
            if self._df is None or self._df.empty:
                return {"machine_id": machine_id, "temperature": 68.0, "vibration": 1.8, "pressure": 100.0, "rpm": 1500, "current": 10.0, "power": 3.8}

            mach_df = self._df[self._df["machine_id"] == machine_id]
            if mach_df.empty:
                return {"error": f"Machine '{machine_id}' not found in telemetry stream."}

            latest_row = mach_df.iloc[-1].to_dict()
            return latest_row

        @self.tool(
            name="get_sensor_history",
            description="Retrieves a historical sequence of sensor readings for trend and degradation curve analysis."
        )
        def get_sensor_history(machine_id: str = "M1000", limit: int = 10) -> list[dict[str, Any]]:
            if self._df is None or self._df.empty:
                return []
            mach_df = self._df[self._df["machine_id"] == machine_id]
            if mach_df.empty:
                return []
            return mach_df.tail(limit).to_dict(orient="records")

        @self.tool(
            name="get_breached_sensors",
            description="Checks if any sensor channels for a machine are breaching normal operating thresholds (vibration > 3.0 mm/s, temperature > 70°C, pressure < 80 PSI)."
        )
        def get_breached_sensors(machine_id: str = "M1000") -> dict[str, Any]:
            telemetry = get_latest_telemetry(machine_id)
            if "error" in telemetry:
                return telemetry

            breaches = []
            if float(telemetry.get("vibration", 0)) > 3.0:
                breaches.append({"sensor": "vibration", "value": telemetry["vibration"], "threshold": 3.0, "severity": "HIGH"})
            if float(telemetry.get("temperature", 0)) > 70.0:
                breaches.append({"sensor": "temperature", "value": telemetry["temperature"], "threshold": 70.0, "severity": "HIGH"})
            if float(telemetry.get("pressure", 100)) < 80.0:
                breaches.append({"sensor": "pressure", "value": telemetry["pressure"], "threshold": 80.0, "severity": "HIGH"})

            return {
                "machine_id": machine_id,
                "is_anomalous": len(breaches) > 0,
                "breaches": breaches,
            }
