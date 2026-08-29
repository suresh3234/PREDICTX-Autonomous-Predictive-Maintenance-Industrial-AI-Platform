import React, { useState } from "react";
import { LineChart as ChartIcon, Eye } from "lucide-react";

export default function TelemetryChart({ telemetry, machineCode }) {
  const [activeChannels, setActiveChannels] = useState({
    temperature: true,
    vibration: true,
    pressure: true,
  });

  // Synthesize a realistic 20-step historical sequence leading to current reading
  const curTemp = telemetry?.temperature || 65;
  const curVib = telemetry?.vibration || 2.0;
  const curPress = telemetry?.pressure || 100;

  const pointsCount = 20;
  const points = [];

  for (let i = pointsCount - 1; i >= 0; i--) {
    const decay = i * 0.05;
    points.push({
      step: pointsCount - i,
      temperature: Math.max(curTemp - (curTemp * 0.25 * (i / pointsCount)) + (Math.sin(i * 0.8) * 1.5), 20),
      vibration: Math.max(curVib - (curVib * 0.4 * (i / pointsCount)) + (Math.cos(i * 1.2) * 0.2), 0.5),
      pressure: Math.max(curPress + (curPress * 0.1 * (i / pointsCount)) + (Math.sin(i * 0.5) * 2), 50),
    });
  }

  // SVG dimensions
  const svgWidth = 800;
  const svgHeight = 220;
  const padding = 30;

  const getCoordinates = (dataKey, minVal, maxVal) => {
    return points.map((p, idx) => {
      const x = padding + (idx / (points.length - 1)) * (svgWidth - padding * 2);
      const val = p[dataKey];
      const normalizedY = (val - minVal) / (maxVal - minVal || 1);
      const y = svgHeight - padding - normalizedY * (svgHeight - padding * 2);
      return `${x},${y}`;
    }).join(" ");
  };

  const tempPath = getCoordinates("temperature", 20, 100);
  const vibPath = getCoordinates("vibration", 0, 5);
  const pressPath = getCoordinates("pressure", 40, 160);

  const toggleChannel = (key) => {
    setActiveChannels((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="glass-panel" style={{ padding: "20px", marginBottom: "24px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
            <ChartIcon size={18} color="var(--accent-cyan)" />
            Historical Multi-Sensor Trend Curve: {machineCode}
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
            Normalized multi-step telemetry trajectory leading to current operational state
          </p>
        </div>

        {/* Channel toggles */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            onClick={() => toggleChannel("temperature")}
            style={{
              background: activeChannels.temperature ? "rgba(6, 182, 212, 0.2)" : "rgba(255, 255, 255, 0.05)",
              color: activeChannels.temperature ? "var(--accent-cyan)" : "var(--text-dim)",
              border: `1px solid ${activeChannels.temperature ? "var(--accent-cyan)" : "var(--border-subtle)"}`,
              borderRadius: "var(--radius-sm)",
              padding: "4px 10px",
              fontSize: "0.75rem",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ● Temperature
          </button>

          <button
            onClick={() => toggleChannel("vibration")}
            style={{
              background: activeChannels.vibration ? "rgba(244, 63, 94, 0.2)" : "rgba(255, 255, 255, 0.05)",
              color: activeChannels.vibration ? "var(--accent-rose)" : "var(--text-dim)",
              border: `1px solid ${activeChannels.vibration ? "var(--accent-rose)" : "var(--border-subtle)"}`,
              borderRadius: "var(--radius-sm)",
              padding: "4px 10px",
              fontSize: "0.75rem",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ● Vibration
          </button>

          <button
            onClick={() => toggleChannel("pressure")}
            style={{
              background: activeChannels.pressure ? "rgba(59, 130, 246, 0.2)" : "rgba(255, 255, 255, 0.05)",
              color: activeChannels.pressure ? "var(--accent-blue)" : "var(--text-dim)",
              border: `1px solid ${activeChannels.pressure ? "var(--accent-blue)" : "var(--border-subtle)"}`,
              borderRadius: "var(--radius-sm)",
              padding: "4px 10px",
              fontSize: "0.75rem",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ● Pressure
          </button>
        </div>
      </div>

      {/* SVG Multi-Line Chart */}
      <div style={{ width: "100%", overflowX: "auto" }}>
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ width: "100%", height: "200px", display: "block" }}
        >
          {/* Grid lines */}
          <line x1={padding} y1={padding} x2={svgWidth - padding} y2={padding} stroke="rgba(255,255,255,0.06)" strokeDasharray="4" />
          <line x1={padding} y1={svgHeight / 2} x2={svgWidth - padding} y2={svgHeight / 2} stroke="rgba(255,255,255,0.06)" strokeDasharray="4" />
          <line x1={padding} y1={svgHeight - padding} x2={svgWidth - padding} y2={svgHeight - padding} stroke="rgba(255,255,255,0.12)" />

          {/* Temperature Line */}
          {activeChannels.temperature && (
            <polyline
              fill="none"
              stroke="var(--accent-cyan)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              points={tempPath}
            />
          )}

          {/* Vibration Line */}
          {activeChannels.vibration && (
            <polyline
              fill="none"
              stroke="var(--accent-rose)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              points={vibPath}
            />
          )}

          {/* Pressure Line */}
          {activeChannels.pressure && (
            <polyline
              fill="none"
              stroke="var(--accent-blue)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              points={pressPath}
            />
          )}

          {/* Current reading marker pulse dot */}
          <circle
            cx={svgWidth - padding}
            cy={activeChannels.vibration ? getCoordinates("vibration", 0, 5).split(" ").pop().split(",")[1] : svgHeight / 2}
            r="5"
            fill="var(--accent-rose)"
            style={{ filter: "drop-shadow(0 0 6px var(--accent-rose))" }}
          />
        </svg>
      </div>
    </div>
  );
}
