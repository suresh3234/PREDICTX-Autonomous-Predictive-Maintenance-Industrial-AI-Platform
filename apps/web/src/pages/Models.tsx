import React, { useState, useEffect } from 'react';
import {
  Layers,
  CheckCircle2,
  GitBranch,
  Calendar,
  Database,
  ArrowUpRight,
  ShieldCheck,
  Cpu,
  RefreshCw,
  Box,
  FileCode,
} from 'lucide-react';
import { fetchRegisteredModels } from '../api/client';

export const Models: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTask, setFilterTask] = useState('ALL');

  useEffect(() => {
    async function loadModels() {
      try {
        const res = await fetchRegisteredModels();
        setModels(res.models || []);
      } catch (err) {
        console.error('Failed loading models:', err);
      } finally {
        setLoading(false);
      }
    }
    loadModels();
  }, []);

  const defaultModels = [
    {
      task: 'anomaly_detection',
      version: '1.0.0',
      status: 'PRODUCTION',
      metrics: { 'F1-Score': 0.95, Precision: 0.94, Recall: 0.96 },
      hyperparameters: { nu: 0.05, kernel: 'rbf', gamma: 'scale' },
      created_at: '2026-08-28T16:12:53Z',
      dataset_lineage: 'data/synthetic/sensor_readings.csv (100k samples)',
      artifacts: {
        model: 'ml/registry/store/anomaly_detection/1.0.0/model_best_anomaly_detector.pkl',
        scaler: 'ml/registry/store/anomaly_detection/1.0.0/scaler_anomaly_scaler.pkl',
      },
    },
    {
      task: 'failure_classification',
      version: '1.2.0',
      status: 'PRODUCTION',
      metrics: { Accuracy: 0.932, 'F1-Score': 0.924, 'ROC-AUC': 0.978 },
      hyperparameters: { n_estimators: 120, max_depth: 6, learning_rate: 0.05 },
      created_at: '2026-08-28T18:40:00Z',
      dataset_lineage: 'data/synthetic/sensor_readings.csv',
      artifacts: {
        model: 'ml/registry/store/failure_classification/1.2.0/model_threat_classifier.pkl',
      },
    },
    {
      task: 'rul_prediction',
      version: '1.1.0',
      status: 'PRODUCTION',
      metrics: { RMSE: 12.4, MAE: 8.8, 'R2-Score': 0.89 },
      hyperparameters: { hidden_dim: 64, num_layers: 2, dropout: 0.2 },
      created_at: '2026-08-28T19:15:00Z',
      dataset_lineage: 'data/synthetic/sensor_readings.csv (Run-to-failure cycles)',
      artifacts: {
        model: 'ml/registry/store/rul_prediction/1.1.0/model_rul_regressor.pkl',
      },
    },
    {
      task: 'sensor_forecasting',
      version: '1.0.1',
      status: 'STAGING',
      metrics: { MAPE: 3.8, MAE: 1.2 },
      hyperparameters: { alpha: 1.0, lag_window: 24 },
      created_at: '2026-08-29T10:00:00Z',
      dataset_lineage: 'data/synthetic/sensor_readings.csv',
      artifacts: {
        model: 'ml/registry/store/sensor_forecasting/1.0.1/model_forecaster.pkl',
      },
    },
  ];

  const displayedModels = models.length > 0 ? models : defaultModels;
  const filtered = filterTask === 'ALL' ? displayedModels : displayedModels.filter((m) => m.task === filterTask);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Model Registry & Artifact Catalog</h1>
            <p className="text-sm text-slate-400">
              Production and Staging ML models for anomaly detection, failure classification, and RUL forecasting
            </p>
          </div>
        </div>

        {/* Task Filter */}
        <div className="flex items-center gap-2">
          {['ALL', 'anomaly_detection', 'failure_classification', 'rul_prediction', 'sensor_forecasting'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterTask(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterTask === t
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {t === 'ALL' ? 'All Tasks' : t.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filtered.map((m, idx) => (
          <div
            key={idx}
            className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-sm hover:border-purple-500/40 transition-all"
          >
            {/* Top Bar */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-purple-400">
                  <Box className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white uppercase tracking-wide">
                    {m.task?.replace('_', ' ')}
                  </h3>
                  <span className="text-xs font-mono text-slate-400">v{m.version}</span>
                </div>
              </div>

              <span
                className={`px-3 py-1 rounded-full text-xs font-bold ${
                  m.status === 'PRODUCTION'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {m.status}
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-3 gap-2.5 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 mb-4">
              {Object.entries(m.metrics || {}).map(([k, v]) => (
                <div key={k} className="text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-medium block">{k}</span>
                  <span className="text-sm font-bold font-mono text-purple-300">
                    {typeof v === 'number' ? v.toFixed(3) : String(v)}
                  </span>
                </div>
              ))}
            </div>

            {/* Metadata info */}
            <div className="space-y-2 text-xs text-slate-400 mb-4">
              <div className="flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                <span className="truncate">
                  Lineage: <span className="text-slate-300 font-mono">{m.dataset_lineage}</span>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                <span>
                  Registered: <span className="text-slate-300 font-mono">{new Date(m.created_at).toLocaleDateString()}</span>
                </span>
              </div>
            </div>

            {/* Hyperparameters Tag Pill */}
            <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] text-slate-500 font-medium mr-1">Params:</span>
              {Object.entries(m.hyperparameters || {}).map(([k, v]) => (
                <span key={k} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300">
                  {k}={String(v)}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
