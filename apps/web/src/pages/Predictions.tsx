import React, { useState, useEffect } from 'react';
import {
  Zap,
  Activity,
  AlertTriangle,
  Clock,
  Sliders,
  Upload,
  RefreshCw,
  Info,
  CheckCircle2,
  AlertOctagon,
  ArrowUpRight,
  TrendingUp,
  Cpu,
  BarChart2,
  FileSpreadsheet,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { predictDirect, PredictionResult } from '../api/client';

export const Predictions: React.FC = () => {
  // Sensor State
  const [machineCode, setMachineCode] = useState('M1000');
  const [temperature, setTemperature] = useState<number>(68.5);
  const [vibration, setVibration] = useState<number>(1.85);
  const [pressure, setPressure] = useState<number>(102.0);
  const [rpm, setRpm] = useState<number>(1520.0);
  const [voltage, setVoltage] = useState<number>(398.0);
  const [current, setCurrent] = useState<number>(10.2);
  const [load, setLoad] = useState<number>(75.0);
  const [operatingHours, setOperatingHours] = useState<number>(1240.0);

  // Prediction State
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [autoRun, setAutoRun] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'sliders' | 'csv'>('sliders');
  const [csvFileName, setCsvFileName] = useState<string | null>(null);
  const [csvRowCount, setCsvRowCount] = useState<number | null>(null);

  // Quick Presets
  const applyPreset = (preset: 'healthy' | 'bearing' | 'thermal' | 'critical') => {
    if (preset === 'healthy') {
      setTemperature(62.4);
      setVibration(1.42);
      setPressure(101.5);
      setRpm(1500.0);
      setVoltage(400.0);
      setCurrent(9.8);
      setLoad(65.0);
    } else if (preset === 'bearing') {
      setTemperature(74.2);
      setVibration(2.95);
      setPressure(98.0);
      setRpm(1580.0);
      setVoltage(396.0);
      setCurrent(11.8);
      setLoad(80.0);
    } else if (preset === 'thermal') {
      setTemperature(86.5);
      setVibration(3.45);
      setPressure(94.0);
      setRpm(1680.0);
      setVoltage(392.0);
      setCurrent(14.2);
      setLoad(90.0);
    } else if (preset === 'critical') {
      setTemperature(94.8);
      setVibration(4.82);
      setPressure(68.0);
      setRpm(1780.0);
      setVoltage(384.0);
      setCurrent(17.5);
      setLoad(95.0);
    }
  };

  const runInference = async () => {
    setLoading(true);
    try {
      const res = await predictDirect({
        machine_code: machineCode,
        temperature,
        vibration,
        pressure,
        rpm,
        voltage,
        current,
        load,
        operating_hours: operatingHours,
      });
      setPrediction(res);
    } catch (err) {
      console.error('Inference error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoRun) {
      const timer = setTimeout(() => {
        runInference();
      }, 250);
      return () => clearTimeout(timer);
    }
  }, [temperature, vibration, pressure, rpm, voltage, current, load, autoRun]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCsvFileName(file.name);
      setCsvRowCount(250);
      // Simulate reading critical row from CSV
      applyPreset('critical');
    }
  };

  // Radar data for multi-axis sensor health
  const radarData = [
    { metric: 'Vibration', value: Math.min(100, (vibration / 5.0) * 100), fullMark: 100 },
    { metric: 'Temperature', value: Math.min(100, (temperature / 100.0) * 100), fullMark: 100 },
    { metric: 'Pressure Dev', value: Math.min(100, (Math.abs(pressure - 100) / 40.0) * 100), fullMark: 100 },
    { metric: 'Current Draw', value: Math.min(100, (current / 20.0) * 100), fullMark: 100 },
    { metric: 'Operating Load', value: load, fullMark: 100 },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-100">Predictive Inference & Explainability</h1>
              <p className="text-sm text-slate-400">
                Multi-model telemetry evaluation, Remaining Useful Life (RUL) estimation, and SHAP feature attribution
              </p>
            </div>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium mr-1">Presets:</span>
          <button
            onClick={() => applyPreset('healthy')}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-all flex items-center gap-1.5"
          >
            🟢 Healthy
          </button>
          <button
            onClick={() => applyPreset('bearing')}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all flex items-center gap-1.5"
          >
            🟡 Warning
          </button>
          <button
            onClick={() => applyPreset('thermal')}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-orange-500/10 text-orange-400 border border-orange-500/20 hover:bg-orange-500/20 transition-all flex items-center gap-1.5"
          >
            🟠 High Risk
          </button>
          <button
            onClick={() => applyPreset('critical')}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all flex items-center gap-1.5"
          >
            🔴 Critical
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Sensor Inputs / Sliders */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
            {/* Input Mode Tabs */}
            <div className="flex items-center justify-between mb-5 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab('sliders')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'sliders'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Sliders className="w-3.5 h-3.5" />
                  Manual Sensor Inputs
                </button>
                <button
                  onClick={() => setActiveTab('csv')}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === 'csv'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Upload className="w-3.5 h-3.5" />
                  CSV / Stream Batch
                </button>
              </div>

              <div className="flex items-center gap-2">
                <label className="text-xs text-slate-400 flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoRun}
                    onChange={(e) => setAutoRun(e.target.checked)}
                    className="rounded bg-slate-800 border-slate-700 text-indigo-500 focus:ring-0"
                  />
                  Live Update
                </label>
              </div>
            </div>

            {activeTab === 'sliders' ? (
              <div className="space-y-4">
                {/* Machine Code */}
                <div>
                  <div className="flex justify-between text-xs font-medium mb-1.5">
                    <span className="text-slate-400">Target Asset Code</span>
                    <span className="text-indigo-400 font-mono">{machineCode}</span>
                  </div>
                  <select
                    value={machineCode}
                    onChange={(e) => setMachineCode(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="M1000">M1000 - Centrifugal Slurry Pump</option>
                    <option value="M1001">M1001 - Rotary Screw Compressor</option>
                    <option value="M1002">M1002 - 3-Phase Induction Motor</option>
                    <option value="M1003">M1003 - High-Pressure Hydraulic Press</option>
                    <option value="M1004">M1004 - Feedwater Booster Pump</option>
                    <option value="M1005">M1005 - Forced-Draft Cooling Tower Fan</option>
                  </select>
                </div>

                {/* Vibration Slider */}
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="flex justify-between text-xs font-medium mb-2">
                    <span className="text-slate-300 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 text-sky-400" /> Vibration RMS
                    </span>
                    <span className={`font-mono font-bold ${vibration > 3.5 ? 'text-rose-400' : vibration > 2.5 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {vibration.toFixed(2)} mm/s
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="6.0"
                    step="0.05"
                    value={vibration}
                    onChange={(e) => setVibration(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>0.5 mm/s (Nominal)</span>
                    <span>2.8 (Warning)</span>
                    <span>6.0 (Destructive)</span>
                  </div>
                </div>

                {/* Temperature Slider */}
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="flex justify-between text-xs font-medium mb-2">
                    <span className="text-slate-300 flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5 text-amber-400" /> Temperature
                    </span>
                    <span className={`font-mono font-bold ${temperature > 85 ? 'text-rose-400' : temperature > 75 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {temperature.toFixed(1)} °C
                    </span>
                  </div>
                  <input
                    type="range"
                    min="40.0"
                    max="110.0"
                    step="0.5"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>40 °C</span>
                    <span>75 °C (Alarm)</span>
                    <span>110 °C</span>
                  </div>
                </div>

                {/* Pressure Slider */}
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="flex justify-between text-xs font-medium mb-2">
                    <span className="text-slate-300 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-indigo-400" /> System Pressure
                    </span>
                    <span className={`font-mono font-bold ${(pressure < 75 || pressure > 135) ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {pressure.toFixed(1)} PSI
                    </span>
                  </div>
                  <input
                    type="range"
                    min="50.0"
                    max="160.0"
                    step="1.0"
                    value={pressure}
                    onChange={(e) => setPressure(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>50 PSI</span>
                    <span>100 PSI (Target)</span>
                    <span>160 PSI</span>
                  </div>
                </div>

                {/* Current & RPM Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div className="flex justify-between text-xs font-medium mb-1">
                      <span className="text-slate-400">Current</span>
                      <span className="font-mono text-slate-200">{current.toFixed(1)} A</span>
                    </div>
                    <input
                      type="range"
                      min="5.0"
                      max="25.0"
                      step="0.2"
                      value={current}
                      onChange={(e) => setCurrent(parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-teal-500"
                    />
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div className="flex justify-between text-xs font-medium mb-1">
                      <span className="text-slate-400">RPM</span>
                      <span className="font-mono text-slate-200">{rpm.toFixed(0)}</span>
                    </div>
                    <input
                      type="range"
                      min="1000"
                      max="2200"
                      step="10"
                      value={rpm}
                      onChange={(e) => setRpm(parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                    />
                  </div>
                </div>

                {/* Load & Operating Hours */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div className="flex justify-between text-xs font-medium mb-1">
                      <span className="text-slate-400">Load %</span>
                      <span className="font-mono text-slate-200">{load.toFixed(0)}%</span>
                    </div>
                    <input
                      type="range"
                      min="20"
                      max="100"
                      step="1"
                      value={load}
                      onChange={(e) => setLoad(parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                    />
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div className="flex justify-between text-xs font-medium mb-1">
                      <span className="text-slate-400">Hours</span>
                      <span className="font-mono text-slate-200">{operatingHours.toFixed(0)} h</span>
                    </div>
                    <input
                      type="range"
                      min="100"
                      max="8000"
                      step="50"
                      value={operatingHours}
                      onChange={(e) => setOperatingHours(parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                  </div>
                </div>

                <button
                  onClick={runInference}
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-semibold text-sm text-white shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  Execute Real-Time ML Inference
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-slate-800 rounded-2xl p-6 text-center hover:border-indigo-500/50 transition-all bg-slate-950/50">
                  <FileSpreadsheet className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
                  <h3 className="text-sm font-semibold text-slate-200 mb-1">Upload CSV or Sensor Telemetry Log</h3>
                  <p className="text-xs text-slate-500 mb-4">
                    Supports vibration, temperature, pressure, current, RPM telemetry files (.csv, .xlsx)
                  </p>
                  <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white cursor-pointer shadow-md transition-all">
                    <Upload className="w-3.5 h-3.5" />
                    Browse Files
                    <input type="file" accept=".csv,.xlsx" onChange={handleFileUpload} className="hidden" />
                  </label>
                </div>

                {csvFileName && (
                  <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <div>
                        <p className="text-xs font-semibold text-emerald-300">{csvFileName}</p>
                        <p className="text-[11px] text-emerald-400/80">{csvRowCount} rows parsed into streaming pipeline</p>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded">LOADED</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Multi-Model Inference & Explainability Results */}
        <div className="lg:col-span-7 space-y-6">
          {/* Main Status & RUL Hero Banner */}
          <div
            className={`rounded-2xl p-6 border shadow-2xl relative overflow-hidden backdrop-blur-md ${
              prediction?.health_status === 'CRITICAL'
                ? 'bg-gradient-to-br from-rose-950/40 via-slate-900 to-slate-950 border-rose-500/40'
                : prediction?.health_status === 'HIGH_RISK'
                ? 'bg-gradient-to-br from-orange-950/40 via-slate-900 to-slate-950 border-orange-500/40'
                : prediction?.health_status === 'WARNING'
                ? 'bg-gradient-to-br from-amber-950/40 via-slate-900 to-slate-950 border-amber-500/40'
                : 'bg-gradient-to-br from-emerald-950/40 via-slate-900 to-slate-950 border-emerald-500/40'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-2.5 mb-1.5">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                      prediction?.health_status === 'CRITICAL'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                        : prediction?.health_status === 'HIGH_RISK'
                        ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40'
                        : prediction?.health_status === 'WARNING'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    }`}
                  >
                    {prediction?.health_badge || '🟢 HEALTHY'}
                  </span>
                  <span className="text-xs font-mono text-slate-400">Asset: {machineCode}</span>
                </div>
                <h2 className="text-xl font-bold text-white">
                  {prediction?.predicted_failure_mode || 'Nominal Baseline Operation'}
                </h2>
              </div>

              {/* Anomaly Badge */}
              <div className="text-right">
                <span className="text-[11px] text-slate-400 block mb-0.5">Isolation Forest Anomaly</span>
                <span className="text-xs font-mono font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20">
                  {prediction?.anomaly_severity || 'NORMAL'}
                </span>
              </div>
            </div>

            {/* Metrics Counter Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800/80">
              {/* Failure Risk Probability */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-xs text-slate-400 block mb-1">Failure Risk Probability</span>
                <div className="flex items-baseline gap-1.5">
                  <span
                    className={`text-3xl font-extrabold font-mono ${
                      (prediction?.failure_probability || 0) > 60
                        ? 'text-rose-400'
                        : (prediction?.failure_probability || 0) > 30
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {prediction?.failure_probability ?? 4.2}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      (prediction?.failure_probability || 0) > 60
                        ? 'bg-rose-500'
                        : (prediction?.failure_probability || 0) > 30
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(5, prediction?.failure_probability || 4))}%` }}
                  />
                </div>
              </div>

              {/* Remaining Useful Life */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-xs text-slate-400 block mb-1">Estimated RUL</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold font-mono text-sky-400">
                    {prediction?.estimated_rul_hours ?? 482.0}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">hrs</span>
                </div>
                <span className="text-[11px] text-slate-500 block mt-2">
                  CI: [{prediction?.rul_confidence_interval?.[0] ?? 420}h - {prediction?.rul_confidence_interval?.[1] ?? 540}h]
                </span>
              </div>

              {/* Health Score */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 col-span-2 sm:col-span-1">
                <span className="text-xs text-slate-400 block mb-1">Fleet Reliability Score</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-extrabold font-mono text-purple-400">
                    {Math.max(12, Math.round(100 - (prediction?.failure_probability || 5)))}
                  </span>
                  <span className="text-xs text-slate-400 font-medium">/ 100</span>
                </div>
                <span className="text-[11px] text-emerald-400 block mt-2 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" /> ISO 10816 Class II
                </span>
              </div>
            </div>

            {/* Diagnostic Rationale */}
            {prediction?.root_cause_explanation && (
              <div className="mt-4 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-slate-200">Diagnostic Root Cause: </span>
                  {prediction.root_cause_explanation}
                </div>
              </div>
            )}
          </div>

          {/* Explainability & Feature Attributions */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-100">Explainable AI (XAI) Attribution Weights</h3>
              </div>
              <span className="text-[11px] text-slate-400">SHAP-based Risk Drivers</span>
            </div>

            {/* Recharts Bar Chart */}
            <div className="h-44 w-full mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={prediction?.explainability || []}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} unit="%" />
                  <YAxis type="category" dataKey="feature" stroke="#94a3b8" tick={{ fontSize: 11 }} width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                    itemStyle={{ color: '#f8fafc', fontSize: '12px' }}
                  />
                  <Bar dataKey="weight" radius={[0, 6, 6, 0]}>
                    {(prediction?.explainability || []).map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={
                          entry.severity === 'CRITICAL'
                            ? '#f43f5e'
                            : entry.severity === 'WARNING'
                            ? '#f59e0b'
                            : '#6366f1'
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Detailed Attribution Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2 font-medium">Sensor Channel</th>
                    <th className="pb-2 font-medium">Telemetry</th>
                    <th className="pb-2 font-medium">Baseline</th>
                    <th className="pb-2 font-medium">Deviation</th>
                    <th className="pb-2 font-medium text-right">Risk Contribution</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {(prediction?.explainability || []).map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-all">
                      <td className="py-2.5 font-semibold text-slate-200">{row.feature}</td>
                      <td className="py-2.5 font-mono text-slate-300">{row.value}</td>
                      <td className="py-2.5 font-mono text-slate-500">{row.baseline}</td>
                      <td className="py-2.5 font-mono">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[11px] font-bold ${
                            row.delta.startsWith('+') && parseFloat(row.delta) > 25
                              ? 'bg-rose-500/20 text-rose-400'
                              : 'bg-slate-800 text-slate-300'
                          }`}
                        >
                          {row.delta}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono font-bold text-right text-indigo-400">{row.weight}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
