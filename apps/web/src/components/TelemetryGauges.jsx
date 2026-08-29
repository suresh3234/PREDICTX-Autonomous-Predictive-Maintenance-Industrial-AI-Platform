import React from "react";
import { Thermometer, Zap, Gauge, RefreshCw, Disc, Activity, Droplets, Wrench } from "lucide-react";

export default function TelemetryGauges({ telemetry }) {
  if (!telemetry) {
    return (
      <div className="glass-panel" style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
        Loading telemetry stream...
      </div>
    );
  }

  const {
    temperature = 0,
    vibration = 0,
    pressure = 0,
    rpm = 0,
    voltage = 0,
    current = 0,
    power = 0,
    humidity = 0,
    load = 0,
    operating_hours = 0,
    maintenance_count = 0,
    timestamp = "",
  } = telemetry;

  const sensors = [
    {
      label: "Process Temperature",
      value: `${temperature.toFixed(1)}°C`,
      icon: Thermometer,
      color: temperature > 70 ? "var(--accent-rose)" : "var(--accent-cyan)",
      desc: temperature > 70 ? "High Thermal Load" : "Nominal Cooling",
      progress: Math.min((temperature / 100) * 100, 100),
    },
    {
      label: "Vibration RMS",
      value: `${vibration.toFixed(2)} mm/s`,
      icon: Activity,
      color: vibration > 3.0 ? "var(--accent-rose)" : "var(--accent-emerald)",
      desc: vibration > 3.0 ? "Bearing Anomaly" : "Balanced Dynamics",
      progress: Math.min((vibration / 5) * 100, 100),
    },
    {
      label: "Hydraulic Pressure",
      value: `${pressure.toFixed(1)} PSI`,
      icon: Gauge,
      color: pressure < 80 ? "var(--accent-amber)" : "var(--accent-blue)",
      desc: pressure < 80 ? "Low Pressure Alert" : "Steady Chamber",
      progress: Math.min((pressure / 150) * 100, 100),
    },
    {
      label: "Spindle Speed",
      value: `${Math.round(rpm)} RPM`,
      icon: Disc,
      color: "var(--accent-violet)",
      desc: "Synchronous Drive",
      progress: Math.min((rpm / 3000) * 100, 100),
    },
    {
      label: "Power Consumption",
      value: `${power.toFixed(2)} kW`,
      icon: Zap,
      color: "var(--accent-amber)",
      desc: `${voltage.toFixed(0)}V / ${current.toFixed(1)}A`,
      progress: Math.min((power / 5) * 100, 100),
    },
    {
      label: "Operational Load",
      value: `${load.toFixed(1)}%`,
      icon: RefreshCw,
      color: load > 85 ? "var(--accent-rose)" : "var(--accent-cyan)",
      desc: `${operating_hours.toFixed(1)} Operating Hours`,
      progress: Math.min(load, 100),
    },
  ];

  return (
    <div style={{ marginBottom: "24px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
          <Gauge size={18} color="var(--accent-cyan)" />
          Real-Time Sensor Telemetry
        </h2>
        <span style={{ fontSize: "0.75rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
          Last Recorded Timestamp: {timestamp || "Live"}
        </span>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
        gap: "14px",
      }}>
        {sensors.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className="glass-panel"
              style={{
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: "500" }}>
                    {s.label}
                  </span>
                  <div style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "var(--radius-sm)",
                    background: "rgba(255, 255, 255, 0.05)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}>
                    <Icon size={16} color={s.color} />
                  </div>
                </div>

                <div style={{ fontSize: "1.4rem", fontWeight: "800", color: "var(--text-main)", marginBottom: "4px" }}>
                  {s.value}
                </div>

                <div style={{ fontSize: "0.72rem", color: "var(--text-dim)", marginBottom: "10px" }}>
                  {s.desc}
                </div>
              </div>

              {/* Progress meter bar */}
              <div style={{
                width: "100%",
                height: "4px",
                background: "rgba(255, 255, 255, 0.06)",
                borderRadius: "999px",
                overflow: "hidden",
              }}>
                <div style={{
                  width: `${s.progress}%`,
                  height: "100%",
                  background: s.color,
                  borderRadius: "999px",
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
