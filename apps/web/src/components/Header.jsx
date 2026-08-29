import React from "react";
import { Activity, Cpu, Bot, RefreshCw, Layers, ShieldCheck } from "lucide-react";

export default function Header({
  machinesCount,
  selectedMachine,
  onRefresh,
  onOpenCopilot,
  onOpenRetrain,
  backendConnected,
}) {
  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "16px 28px",
      borderBottom: "1px solid var(--border-subtle)",
      background: "rgba(11, 15, 25, 0.8)",
      backdropFilter: "blur(20px)",
      position: "sticky",
      top: 0,
      zIndex: 40,
    }}>
      {/* Brand & Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div style={{
          width: "42px",
          height: "42px",
          borderRadius: "var(--radius-md)",
          background: "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 20px rgba(6, 182, 212, 0.4)",
        }}>
          <Activity size={24} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <h1 style={{ fontSize: "1.4rem", fontWeight: "800", letterSpacing: "-0.03em" }}>
              Predict<span className="gradient-text">X</span>
            </h1>
            <span className="badge badge-normal" style={{ fontSize: "0.65rem", padding: "2px 8px" }}>
              v1.0 Prod
            </span>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Autonomous Predictive Maintenance & Reliability Intelligence
          </p>
        </div>
      </div>

      {/* Fleet KPI Quick Bar */}
      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", background: "var(--bg-glass)", padding: "6px 14px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
          <Cpu size={16} color="var(--accent-cyan)" />
          <div>
            <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", textTransform: "uppercase" }}>Monitored Fleet</div>
            <div style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--text-main)" }}>
              {machinesCount} Machines Active
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px", background: "var(--bg-glass)", padding: "6px 14px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
          <ShieldCheck size={16} color="var(--accent-emerald)" />
          <div>
            <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", textTransform: "uppercase" }}>Backend API</div>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", fontWeight: "600", color: backendConnected ? "#34d399" : "#fb7185" }}>
              <span className={`pulse-dot ${backendConnected ? "pulse-dot-green" : "pulse-dot-red"}`} />
              {backendConnected ? "Online (Port 8000)" : "Connecting..."}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action Navigation */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          title="Refresh telemetry stream"
          style={{ padding: "8px 12px" }}
        >
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenRetrain}
          style={{ padding: "8px 14px" }}
        >
          <Layers size={16} color="var(--accent-cyan)" />
          <span>MLOps / Retrain</span>
        </button>

        <button
          className="btn btn-primary"
          onClick={onOpenCopilot}
          style={{ padding: "8px 16px" }}
        >
          <Bot size={18} />
          <span>AI Copilot</span>
        </button>
      </div>
    </header>
  );
}
