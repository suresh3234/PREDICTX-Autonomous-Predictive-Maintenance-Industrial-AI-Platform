import React from "react";
import { AlertTriangle, Clock, Activity, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function PredictionsPanel({ predictions, machineCode }) {
  if (!predictions) {
    return (
      <div className="glass-panel" style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)" }}>
        Loading real-time predictive models...
      </div>
    );
  }

  const {
    anomaly_severity = "NORMAL",
    failure_probability = 0.02,
    failure_type = "Healthy Baseline",
    predicted_rul = 45.0,
  } = predictions;

  const failPercent = Math.min(Math.round(failure_probability * 100), 100);

  // Severity theme
  let severityColor = "var(--accent-emerald)";
  if (anomaly_severity === "CRITICAL" || anomaly_severity === "HIGH") {
    severityColor = "var(--accent-rose)";
  } else if (anomaly_severity === "MEDIUM" || anomaly_severity === "LOW") {
    severityColor = "var(--accent-amber)";
  }

  // RUL color
  let rulColor = "var(--accent-emerald)";
  if (predicted_rul <= 6.0) {
    rulColor = "var(--accent-rose)";
  } else if (predicted_rul <= 24.0) {
    rulColor = "var(--accent-amber)";
  }

  return (
    <div className="glass-panel" style={{ padding: "22px", marginBottom: "24px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "18px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "var(--radius-sm)",
            background: "rgba(6, 182, 212, 0.15)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <Activity size={20} color="var(--accent-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: "700" }}>
              Live AI Predictive Insights: <span style={{ color: "var(--accent-cyan)" }}>{machineCode}</span>
            </h3>
            <p style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
              Inference from active production models in the registry
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Diagnosed Condition:</span>
          <span style={{
            fontSize: "0.85rem",
            fontWeight: "700",
            padding: "4px 12px",
            borderRadius: "var(--radius-sm)",
            background: failure_type === "Healthy Baseline" || failure_type === "No Active Threat" ? "rgba(16, 185, 129, 0.15)" : "rgba(244, 63, 94, 0.15)",
            color: failure_type === "Healthy Baseline" || failure_type === "No Active Threat" ? "#34d399" : "#fb7185",
            border: `1px solid ${failure_type === "Healthy Baseline" || failure_type === "No Active Threat" ? "rgba(16, 185, 129, 0.3)" : "rgba(244, 63, 94, 0.3)"}`,
          }}>
            {failure_type}
          </span>
        </div>
      </div>

      {/* 3 Metrics Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        
        {/* 1. Anomaly Status */}
        <div style={{
          background: "var(--bg-glass)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)",
          padding: "16px",
          position: "relative",
          overflow: "hidden",
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
              <ShieldAlert size={15} color={severityColor} />
              Anomaly Detection
            </span>
            <span className={`badge ${anomaly_severity === "NORMAL" ? "badge-normal" : "badge-critical"}`}>
              {anomaly_severity}
            </span>
          </div>

          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: severityColor, marginBottom: "8px" }}>
            {anomaly_severity}
          </div>

          <div style={{
            width: "100%",
            height: "6px",
            background: "rgba(255, 255, 255, 0.08)",
            borderRadius: "999px",
            overflow: "hidden",
          }}>
            <div style={{
              width: anomaly_severity === "CRITICAL" ? "100%" : anomaly_severity === "HIGH" ? "75%" : anomaly_severity === "MEDIUM" ? "50%" : anomaly_severity === "LOW" ? "25%" : "8%",
              height: "100%",
              background: severityColor,
              borderRadius: "999px",
              transition: "width 0.5s ease",
            }} />
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: "6px" }}>
            Unsupervised PyTorch Autoencoder reconstruction threshold
          </div>
        </div>

        {/* 2. Failure Risk Probability */}
        <div style={{
          background: "var(--bg-glass)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)",
          padding: "16px",
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
              <AlertTriangle size={15} color="var(--accent-amber)" />
              Breakdown Probability
            </span>
            <span style={{ fontSize: "0.8rem", fontWeight: "700", color: failPercent > 35 ? "var(--accent-rose)" : "var(--accent-emerald)" }}>
              {failPercent}% Risk
            </span>
          </div>

          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: failPercent > 35 ? "var(--accent-rose)" : "var(--text-main)", marginBottom: "8px" }}>
            {failPercent}%
          </div>

          <div style={{
            width: "100%",
            height: "6px",
            background: "rgba(255, 255, 255, 0.08)",
            borderRadius: "999px",
            overflow: "hidden",
          }}>
            <div style={{
              width: `${failPercent}%`,
              height: "100%",
              background: failPercent > 35 ? "linear-gradient(90deg, #f59e0b, #ef4444)" : "var(--accent-emerald)",
              borderRadius: "999px",
              transition: "width 0.5s ease",
            }} />
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: "6px" }}>
            Cost-Sensitive XGBoost threshold (Tuned for minimal operational cost)
          </div>
        </div>

        {/* 3. Estimated RUL */}
        <div style={{
          background: "var(--bg-glass)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)",
          padding: "16px",
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
              <Clock size={15} color={rulColor} />
              Remaining Useful Life
            </span>
            <span style={{
              fontSize: "0.75rem",
              fontWeight: "600",
              color: predicted_rul < 12 ? "var(--accent-rose)" : "var(--accent-emerald)",
            }}>
              {predicted_rul < 12 ? "Action Required" : "Nominal"}
            </span>
          </div>

          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: rulColor, marginBottom: "8px" }}>
            {predicted_rul.toFixed(1)} <span style={{ fontSize: "0.9rem", fontWeight: "500", color: "var(--text-dim)" }}>Hours Left</span>
          </div>

          <div style={{
            width: "100%",
            height: "6px",
            background: "rgba(255, 255, 255, 0.08)",
            borderRadius: "999px",
            overflow: "hidden",
          }}>
            <div style={{
              width: `${Math.min(Math.max((predicted_rul / 100) * 100, 5), 100)}%`,
              height: "100%",
              background: rulColor,
              borderRadius: "999px",
              transition: "width 0.5s ease",
            }} />
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: "6px" }}>
            Non-linear Random Forest degradation regression
          </div>
        </div>

      </div>
    </div>
  );
}
