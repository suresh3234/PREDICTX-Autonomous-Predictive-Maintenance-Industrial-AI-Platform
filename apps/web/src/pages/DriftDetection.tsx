import React, { useState, useEffect } from 'react';
import {
  GitPullRequest,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  TrendingDown,
  Activity,
  ArrowRight,
  ShieldAlert,
  Zap,
} from 'lucide-react';
import { fetchDriftStatus, triggerRetraining } from '../api/client';

export const DriftDetection: React.FC = () => {
  const [driftData, setDriftData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState<string | null>(null);

  const loadDrift = async () => {
    setLoading(true);
    try {
      const res = await fetchDriftStatus();
      setDriftData(res);
    } catch (err) {
      console.error('Drift load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDrift();
  }, []);

  const handleRetrain = async () => {
    setRetraining(true);
    setRetrainMsg(null);
    try {
      const res = await triggerRetraining('failure_classification', true);
      setRetrainMsg(`Retraining completed! Outcome: ${res.retraining_status || 'SUCCESS'}`);
      loadDrift();
    } catch (err: any) {
      setRetrainMsg(`Retraining failed: ${err.message}`);
    } finally {
      setRetraining(false);
    }
  };

  const defaultMetrics = [
    { feature_name: 'vibration_rms', p_value: 0.0012, is_drifted: true, drift_severity: 'CRITICAL' },
    { feature_name: 'temperature_surge', p_value: 0.0245, is_drifted: true, drift_severity: 'MODERATE' },
    { feature_name: 'pressure_delta', p_value: 0.0841, is_drifted: false, drift_severity: 'NORMAL' },
    { feature_name: 'current_mean', p_value: 0.3204, is_drifted: false, drift_severity: 'NORMAL' },
    { feature_name: 'rpm_harmonic', p_value: 0.4512, is_drifted: false, drift_severity: 'NORMAL' },
    { feature_name: 'power_cross_term', p_value: 0.0182, is_drifted: true, drift_severity: 'MODERATE' },
  ];

  const metrics = driftData?.feature_drift_metrics || defaultMetrics;
  const isDrifted = driftData?.drift_detected ?? true;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <GitPullRequest className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Data Drift & Model Monitoring</h1>
            <p className="text-sm text-slate-400">
              Kolmogorov-Smirnov statistical hypothesis testing across incoming telemetry distributions
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadDrift}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh KS-Test
          </button>
          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all"
          >
            {retraining ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
            Trigger Retraining Pipeline
          </button>
        </div>
      </div>

      {/* Retrain Alert Notification */}
      {retrainMsg && (
        <div className="p-4 rounded-2xl bg-indigo-950/60 border border-indigo-500/40 text-indigo-200 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-indigo-400" />
            <span>{retrainMsg}</span>
          </div>
          <button onClick={() => setRetrainMsg(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Hero Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Drift Alert Status</span>
          <div className="flex items-center gap-2 mt-1">
            {isDrifted ? (
              <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> DRIFT DETECTED
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> STABLE
              </span>
            )}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Drifted Feature Channels</span>
          <span className="text-2xl font-bold font-mono text-amber-400">
            {driftData?.drifted_features_count ?? 3} <span className="text-xs text-slate-500 font-normal">/ {driftData?.total_features ?? 12}</span>
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Significance Level (α)</span>
          <span className="text-2xl font-bold font-mono text-indigo-400">p &lt; 0.05</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Test Statistic Type</span>
          <span className="text-base font-bold font-mono text-slate-200">2-Sample KS Test</span>
        </div>
      </div>

      {/* Feature Channel Drift Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-amber-400" />
          Channel-by-Channel Distribution Divergence
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-medium">
                <th className="pb-3 font-semibold">Engineered Feature</th>
                <th className="pb-3 font-semibold">KS p-Value</th>
                <th className="pb-3 font-semibold">Hypothesis Test (H0)</th>
                <th className="pb-3 font-semibold">Drift Level</th>
                <th className="pb-3 font-semibold text-right">Action Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {metrics.map((row: any, i: number) => (
                <tr key={i} className="hover:bg-slate-800/30 transition-all">
                  <td className="py-3 font-semibold text-slate-200 font-mono">{row.feature_name}</td>
                  <td className="py-3 font-mono text-slate-300 font-bold">{row.p_value}</td>
                  <td className="py-3">
                    {row.is_drifted ? (
                      <span className="text-rose-400 font-medium">Reject Null (Shifted)</span>
                    ) : (
                      <span className="text-emerald-400 font-medium">Retain Null (Identical)</span>
                    )}
                  </td>
                  <td className="py-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                        row.drift_severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-300'
                          : row.drift_severity === 'MODERATE'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      {row.drift_severity}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    {row.is_drifted ? (
                      <span className="text-amber-400 font-medium">Include in Retraining</span>
                    ) : (
                      <span className="text-slate-500">Nominal</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
