import React, { useState } from "react";
import { X, Layers, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";
import { triggerRetraining } from "../api";

export default function RetrainingModal({ isOpen, onClose }) {
  const [selectedTask, setSelectedTask] = useState("failure_classification");
  const [force, setForce] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleRetrain = async () => {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await triggerRetraining(selectedTask, force);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0, 0, 0, 0.75)",
      backdropFilter: "blur(10px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 60,
      padding: "20px",
    }}>
      <div className="glass-panel" style={{
        width: "560px",
        maxWidth: "100%",
        padding: "28px",
        position: "relative",
        background: "rgba(13, 19, 34, 0.95)",
        border: "1px solid var(--border-subtle)",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7)",
      }}>
        {/* Close button */}
        <button
          onClick={onClose}
          style={{ position: "absolute", top: "20px", right: "20px", background: "transparent", border: "none", color: "var(--text-dim)", cursor: "pointer" }}
        >
          <X size={20} />
        </button>

        {/* Title */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "18px" }}>
          <div style={{
            width: "40px",
            height: "40px",
            borderRadius: "var(--radius-sm)",
            background: "rgba(6, 182, 212, 0.15)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <Layers size={22} color="var(--accent-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.2rem", fontWeight: "700" }}>MLOps Retraining & Drift Monitor</h3>
            <p style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
              Check data drift with Kolmogorov-Smirnov/PSI and retrain candidate models
            </p>
          </div>
        </div>

        {/* Task Selector */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "6px", fontWeight: "600" }}>
            Target Model Task
          </label>
          <select
            value={selectedTask}
            onChange={(e) => setSelectedTask(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 14px",
              background: "rgba(255, 255, 255, 0.05)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-main)",
              fontSize: "0.85rem",
              outline: "none",
            }}
          >
            <option value="failure_classification">Failure Threat Classification (XGBoost / Random Forest)</option>
            <option value="anomaly_detection">Anomaly Detection (One-Class SVM / PyTorch Autoencoder)</option>
            <option value="rul_prediction">Remaining Useful Life Regressor (Random Forest)</option>
          </select>
        </div>

        {/* Options */}
        <div style={{ marginBottom: "22px", display: "flex", alignItems: "center", gap: "10px" }}>
          <input
            type="checkbox"
            id="force-toggle"
            checked={force}
            onChange={(e) => setForce(e.target.checked)}
            style={{ cursor: "pointer", accentColor: "var(--accent-cyan)" }}
          />
          <label htmlFor="force-toggle" style={{ fontSize: "0.85rem", color: "var(--text-main)", cursor: "pointer" }}>
            Force retraining regardless of drift status (Override Baseline Gate)
          </label>
        </div>

        {/* Result Area */}
        {result && (
          <div style={{
            background: result.promoted ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
            border: `1px solid ${result.promoted ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
            borderRadius: "var(--radius-md)",
            padding: "14px",
            marginBottom: "18px",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: "700", fontSize: "0.9rem", color: result.promoted ? "var(--accent-emerald)" : "var(--accent-amber)", marginBottom: "6px" }}>
              {result.promoted ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
              {result.promoted ? "Model Promoted to PRODUCTION!" : "Retraining Completed (Not Promoted)"}
            </div>
            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "4px" }}>
              <div>• Version Registered: <strong style={{ color: "var(--text-main)" }}>{result.version || "N/A"}</strong></div>
              <div>• Drift Alert Level: <strong style={{ color: "var(--accent-cyan)" }}>{result.drift_alert}</strong></div>
              <div>• Promotion Status: <strong style={{ color: result.promoted ? "var(--accent-emerald)" : "var(--accent-amber)" }}>{result.promoted ? "PROMOTED" : "CANDIDATE"}</strong></div>
            </div>
          </div>
        )}

        {error && (
          <div style={{ background: "rgba(244, 63, 94, 0.1)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "var(--radius-md)", padding: "12px", marginBottom: "18px", fontSize: "0.8rem", color: "var(--accent-rose)" }}>
            Error: {error}
          </div>
        )}

        {/* Action button */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
          <button
            className="btn btn-primary"
            onClick={handleRetrain}
            disabled={loading}
          >
            {loading ? <RefreshCw size={16} className="spin" /> : <RefreshCw size={16} />}
            {loading ? "Retraining in Progress..." : "Run Retraining Pipeline"}
          </button>
        </div>
      </div>
    </div>
  );
}
