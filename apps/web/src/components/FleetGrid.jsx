import React from "react";
import { Server, Activity, ArrowRight } from "lucide-react";

export default function FleetGrid({ machines, selectedMachine, onSelectMachine, machineStatuses = {} }) {
  return (
    <div style={{ marginBottom: "24px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: "700", display: "flex", alignItems: "center", gap: "8px" }}>
          <Server size={18} color="var(--accent-cyan)" />
          Industrial Equipment Fleet
        </h2>
        <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Select a machine to inspect real-time sensor streams & predictive analytics
        </span>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
        gap: "14px",
      }}>
        {machines.map((mach) => {
          const isSelected = selectedMachine === mach.machine_code;
          const statusInfo = machineStatuses[mach.machine_code] || {
            severity: "NORMAL",
            rul: 48.0,
            failProb: 0.05,
          };

          let badgeClass = "badge-normal";
          if (statusInfo.severity === "CRITICAL" || statusInfo.severity === "HIGH") {
            badgeClass = "badge-critical";
          } else if (statusInfo.severity === "MEDIUM" || statusInfo.severity === "LOW") {
            badgeClass = "badge-warning";
          }

          return (
            <div
              key={mach.id || mach.machine_code}
              onClick={() => onSelectMachine(mach.machine_code)}
              className="glass-panel"
              style={{
                padding: "16px",
                cursor: "pointer",
                border: isSelected ? "1.5px solid var(--accent-cyan)" : "1px solid var(--border-subtle)",
                boxShadow: isSelected ? "var(--shadow-glow)" : "none",
                background: isSelected ? "var(--bg-card-hover)" : "var(--bg-card)",
                transform: isSelected ? "translateY(-2px)" : "none",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <div style={{ fontSize: "1.05rem", fontWeight: "800", color: isSelected ? "var(--accent-cyan)" : "var(--text-main)" }}>
                  {mach.machine_code}
                </div>
                <span className={`badge ${badgeClass}`}>
                  {statusInfo.severity}
                </span>
              </div>

              <div style={{ fontSize: "0.78rem", color: "var(--text-dim)", marginBottom: "12px" }}>
                {mach.machine_type}
              </div>

              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                paddingTop: "10px",
                borderTop: "1px solid var(--border-subtle)",
                fontSize: "0.75rem",
              }}>
                <div>
                  <span style={{ color: "var(--text-dim)" }}>Est. RUL: </span>
                  <span style={{ fontWeight: "700", color: statusInfo.rul < 12 ? "var(--accent-rose)" : "var(--accent-emerald)" }}>
                    {typeof statusInfo.rul === "number" ? `${statusInfo.rul.toFixed(1)}h` : "48.0h"}
                  </span>
                </div>
                <ArrowRight size={14} color={isSelected ? "var(--accent-cyan)" : "var(--text-dim)"} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
