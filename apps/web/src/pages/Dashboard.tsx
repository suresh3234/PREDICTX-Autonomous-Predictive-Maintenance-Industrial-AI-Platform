import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Clock,
  Cpu,
  Flame,
  Radio,
  RefreshCw,
  Sparkles,
  TrendingDown,
  TrendingUp,
  Zap,
  Sliders,
  SlidersHorizontal,
  ChevronRight,
  Info,
  Layers,
  Wrench,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { HealthScore } from '../components/ui/HealthScore';
import { Button } from '../components/ui/Button';
import { MOCK_MACHINES } from '../api/mockData';
import { predictDirect, PredictionResult } from '../api/client';

const RISK_TIMELINE_DATA = [
  { time: '10:00', M1047: 42, M2083: 20, M4120: 35 },
  { time: '11:00', M1047: 48, M2083: 22, M4120: 38 },
  { time: '12:00', M1047: 56, M2083: 28, M4120: 45 },
  { time: '13:00', M1047: 72, M2083: 34, M4120: 58 },
  { time: '14:00', M1047: 84, M2083: 39, M4120: 68 },
  { time: '15:00', M1047: 87, M2083: 42, M4120: 74 },
];

const HEALTH_DISTRIBUTION = [
  { name: 'Healthy', value: 1104, color: '#10b981', percent: '88.5%' },
  { name: 'Warning', value: 87, color: '#f59e0b', percent: '6.9%' },
  { name: 'Critical', value: 12, color: '#ef4444', percent: '1.0%' },
  { name: 'Offline', value: 45, color: '#64748b', percent: '3.6%' },
];

export const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24H');
  const [selectedPlant, setSelectedPlant] = useState('All Plants');

  // Interactive Live Inference Simulation State
  const [temperature, setTemperature] = useState<number>(68.5);
  const [vibration, setVibration] = useState<number>(1.85);
  const [pressure, setPressure] = useState<number>(102.0);
  const [current, setCurrent] = useState<number>(10.2);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loadingPred, setLoadingPred] = useState<boolean>(false);

  const applyPreset = (type: 'healthy' | 'warning' | 'high_risk' | 'critical') => {
    if (type === 'healthy') {
      setTemperature(62.0);
      setVibration(1.4);
      setPressure(101.0);
      setCurrent(9.5);
    } else if (type === 'warning') {
      setTemperature(74.5);
      setVibration(2.95);
      setPressure(98.0);
      setCurrent(11.8);
    } else if (type === 'high_risk') {
      setTemperature(85.0);
      setVibration(3.6);
      setPressure(93.0);
      setCurrent(14.5);
    } else if (type === 'critical') {
      setTemperature(95.0);
      setVibration(4.85);
      setPressure(65.0);
      setCurrent(17.8);
    }
  };

  const runPrediction = async () => {
    setLoadingPred(true);
    try {
      const res = await predictDirect({
        machine_code: 'M1000',
        temperature,
        vibration,
        pressure,
        rpm: 1520.0,
        voltage: 398.0,
        current,
      });
      setPrediction(res);
    } catch (err) {
      console.error('Inference error:', err);
    } finally {
      setLoadingPred(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      runPrediction();
    }, 200);
    return () => clearTimeout(timer);
  }, [temperature, vibration, pressure, current]);

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Global Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              PredictX Industrial Command Center
            </h1>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              100Hz Sensor Stream Active
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            End-to-End Predictive Maintenance: Ingestion → Validation → ML Inference → RUL → XAI → RAG / Multi-Agent Safety
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <Link to="/predictions">
            <Button size="sm" variant="primary" leftIcon={<Zap className="w-3.5 h-3.5" />}>
              Open Full Prediction Lab
            </Button>
          </Link>
          <Link to="/assistant">
            <Button size="sm" variant="ai" leftIcon={<Sparkles className="w-3.5 h-3.5" />}>
              AI Copilot
            </Button>
          </Link>
        </div>
      </div>

      {/* PROMINENT LIVE INTERACTIVE PREDICTION & DATA INSERTION CARD */}
      <div className="rounded-2xl p-6 bg-gradient-to-br from-slate-900 via-navy-900 to-slate-950 border border-indigo-500/30 shadow-2xl space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400">
                <SlidersHorizontal className="w-4 h-4" />
              </span>
              <h2 className="text-base font-bold text-white">Live Interactive Sensor Ingestion & Risk Evaluation</h2>
            </div>
            <p className="text-xs text-slate-400">
              Adjust sensor inputs or pick presets to evaluate real-time failure probability, RUL, and explainability.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400 font-medium mr-1">Presets:</span>
            <button
              onClick={() => applyPreset('healthy')}
              className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-all"
            >
              🟢 Healthy
            </button>
            <button
              onClick={() => applyPreset('warning')}
              className="px-3 py-1 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-all"
            >
              🟡 Warning
            </button>
            <button
              onClick={() => applyPreset('high_risk')}
              className="px-3 py-1 rounded-lg text-xs font-semibold bg-orange-500/10 text-orange-400 border border-orange-500/20 hover:bg-orange-500/20 transition-all"
            >
              🟠 High Risk
            </button>
            <button
              onClick={() => applyPreset('critical')}
              className="px-3 py-1 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all"
            >
              🔴 Critical
            </button>
          </div>
        </div>

        {/* 2-Column Live Ingestion & ML Output Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: 4 Quick Sliders */}
          <div className="lg:col-span-6 grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="flex justify-between text-xs font-medium mb-1.5">
                <span className="text-slate-400">Vibration (RMS)</span>
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
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="flex justify-between text-xs font-medium mb-1.5">
                <span className="text-slate-400">Temperature</span>
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
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="flex justify-between text-xs font-medium mb-1.5">
                <span className="text-slate-400">Pressure</span>
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
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div className="flex justify-between text-xs font-medium mb-1.5">
                <span className="text-slate-400">Current Draw</span>
                <span className={`font-mono font-bold ${current > 15 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {current.toFixed(1)} A
                </span>
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
          </div>

          {/* Right: Live ML Diagnosis Card */}
          <div className="lg:col-span-6 p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold ${
                    prediction?.health_status === 'CRITICAL'
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : prediction?.health_status === 'HIGH_RISK'
                      ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                      : prediction?.health_status === 'WARNING'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}
                >
                  {prediction?.health_badge || '🟢 HEALTHY'}
                </span>
                <span className="text-xs font-mono text-slate-400">IsolationForest: {prediction?.anomaly_severity || 'NORMAL'}</span>
              </div>

              <div className="grid grid-cols-2 gap-4 my-2">
                <div>
                  <span className="text-[11px] text-slate-400 block">Failure Risk Probability</span>
                  <span className="text-2xl font-extrabold font-mono text-rose-400">
                    {prediction?.failure_probability ?? 4.2}%
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 block">Remaining Useful Life (RUL)</span>
                  <span className="text-2xl font-extrabold font-mono text-sky-400">
                    {prediction?.estimated_rul_hours ?? 482.0} <span className="text-xs text-slate-400">hrs</span>
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 font-medium line-clamp-1 mt-1">
                <strong className="text-slate-100">Failure Mode:</strong> {prediction?.predicted_failure_mode || 'Nominal Baseline'}
              </p>
            </div>

            <div className="pt-3 mt-2 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Explainability: Top driver is {prediction?.explainability?.[0]?.feature || 'Vibration'}</span>
              <Link to="/predictions" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                Full Diagnostic Details <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 6 Key Operational KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card hoverable>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider">Total Fleet</span>
              <Cpu className="w-4 h-4 text-brand-500" />
            </div>
            <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100">1,248</div>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-600 dark:text-emerald-400 mt-1 font-medium">
              <TrendingUp className="w-3 h-3" />
              <span>1,104 Healthy (88.5%)</span>
            </div>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider">At Risk</span>
              <AlertTriangle className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-bold font-mono text-amber-600 dark:text-amber-400">87</div>
            <div className="text-[11px] text-slate-400 mt-1">6.9% of monitored fleet</div>
          </CardContent>
        </Card>

        <Card hoverable className="border-rose-500/30 bg-rose-500/5">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider text-rose-600 dark:text-rose-400 font-semibold">Critical Attention</span>
              <Flame className="w-4 h-4 text-rose-500 animate-pulse" />
            </div>
            <div className="text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">12</div>
            <div className="text-[11px] text-rose-500 font-medium mt-1">Immediate intervention required</div>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider">Active Alerts</span>
              <Activity className="w-4 h-4 text-brand-500" />
            </div>
            <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100">24</div>
            <div className="text-[11px] text-rose-500 font-medium mt-1">5 High Severity Alerts</div>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider">Predicted Failures</span>
              <Zap className="w-4 h-4 text-violet-500" />
            </div>
            <div className="text-2xl font-bold font-mono text-violet-600 dark:text-violet-400">18</div>
            <div className="text-[11px] text-slate-400 mt-1">Within next 24-120 hrs</div>
          </CardContent>
        </Card>

        <Card hoverable>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium uppercase tracking-wider">Fleet Health Index</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">82.4</div>
            <div className="flex items-center gap-1 text-[11px] text-emerald-500 font-medium mt-1">
              <TrendingUp className="w-3 h-3" />
              <span>+3.2% vs last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Health Distribution Donut & Predicted Failure Risk Curves */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Machine Health Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Fleet Health Distribution</CardTitle>
            <span className="text-xs text-slate-400">1,248 Units</span>
          </CardHeader>
          <CardContent className="p-5 flex flex-col justify-between">
            <div className="h-44 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={HEALTH_DISTRIBUTION}
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {HEALTH_DISTRIBUTION.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0d131f', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Distribution Legend */}
            <div className="grid grid-cols-2 gap-2 pt-4 border-t border-slate-100 dark:border-slate-800 text-xs">
              {HEALTH_DISTRIBUTION.map((item) => (
                <div key={item.name} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 dark:bg-navy-900/60">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-slate-700 dark:text-slate-300 font-medium">{item.name}</span>
                  </div>
                  <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">{item.percent}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Right (2 cols): Predicted Failure Risk Timeline */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div>
                <CardTitle>Predicted Failure Probability Timeline</CardTitle>
                <p className="text-xs text-slate-400 mt-0.5">Continuous telemetry degradation trajectory</p>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1.5 text-rose-500 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> M1047 (CNC #4)
                </span>
                <span className="flex items-center gap-1.5 text-amber-500 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> M4120 (Turbine #2)
                </span>
                <span className="flex items-center gap-1.5 text-blue-500 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> M2083 (Pump)
                </span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-5">
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={RISK_TIMELINE_DATA}>
                  <defs>
                    <linearGradient id="colorM1047" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="colorM4120" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} unit="%" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0d131f', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="M1047" stroke="#ef4444" strokeWidth={2.5} fillOpacity={1} fill="url(#colorM1047)" />
                  <Area type="monotone" dataKey="M4120" stroke="#f59e0b" strokeWidth={2} fillOpacity={1} fill="url(#colorM4120)" />
                  <Area type="monotone" dataKey="M2083" stroke="#3b82f6" strokeWidth={1.5} fillOpacity={0} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Equipment Focus Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between w-full">
            <div>
              <CardTitle>Critical Equipment Requiring Immediate Action</CardTitle>
              <p className="text-xs text-slate-400 mt-0.5">Machines with RUL &lt; 200 hours or failure probability &gt; 70%</p>
            </div>
            <Link to="/machines" className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1">
              View All 1,248 Machines <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-navy-900 text-slate-400 border-b border-slate-100 dark:border-slate-800 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Machine</th>
                  <th className="px-5 py-3">Plant Location</th>
                  <th className="px-5 py-3">Health Score</th>
                  <th className="px-5 py-3">Failure Probability</th>
                  <th className="px-5 py-3">Estimated RUL</th>
                  <th className="px-5 py-3">Diagnosed Failure Mode</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {MOCK_MACHINES.slice(0, 4).map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                        <Link to={`/machines/${m.code}`} className="hover:text-brand-500 font-mono">
                          {m.code}
                        </Link>
                        <StatusBadge status={m.status} size="sm" />
                      </div>
                      <div className="text-[11px] text-slate-400">{m.name}</div>
                    </td>
                    <td className="px-5 py-3.5 text-slate-600 dark:text-slate-300 font-medium">{m.plant}</td>
                    <td className="px-5 py-3.5">
                      <HealthScore score={m.healthScore} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 font-mono font-semibold text-slate-900 dark:text-slate-100">
                      <span className={m.failureProbability > 0.7 ? 'text-rose-500 font-bold' : 'text-slate-700 dark:text-slate-300'}>
                        {(m.failureProbability * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono font-medium text-slate-700 dark:text-slate-300">
                      {m.rulHours} Hours
                    </td>
                    <td className="px-5 py-3.5 text-slate-600 dark:text-slate-300">
                      {m.predictedFailureType}
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-2">
                      <Link to={`/machines/${m.code}`}>
                        <Button size="sm" variant="ai" leftIcon={<Bot className="w-3.5 h-3.5" />}>
                          Investigate
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
