import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  Clock,
  Cpu,
  FileSpreadsheet,
  Flame,
  HelpCircle,
  Layers,
  LineChart,
  RotateCcw,
  Sparkles,
  Wrench,
  Zap,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart as RechartsLine,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { HealthScore } from '../components/ui/HealthScore';
import { Button } from '../components/ui/Button';
import { MOCK_MACHINES, MOCK_SHAP_FACTORS, MOCK_INVESTIGATION_TIMELINE } from '../api/mockData';

const SENSOR_TREND_DATA = [
  { time: '14:00', temperature: 65.2, vibration: 1.8, pressure: 101.2, current: 10.2 },
  { time: '14:10', temperature: 67.4, vibration: 2.1, pressure: 100.8, current: 10.6 },
  { time: '14:20', temperature: 71.0, vibration: 2.8, pressure: 99.5, current: 11.4 },
  { time: '14:30', temperature: 74.8, vibration: 3.6, pressure: 98.4, current: 12.8 },
  { time: '14:40', temperature: 77.2, vibration: 4.1, pressure: 98.0, current: 14.2 },
  { time: '14:50', temperature: 78.4, vibration: 4.25, pressure: 98.2, current: 14.8 },
];

export const MachineDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('overview');

  const machine = MOCK_MACHINES.find((m) => m.code === id) || MOCK_MACHINES[0];

  const TABS = [
    { id: 'overview', label: 'Overview' },
    { id: 'telemetry', label: 'Sensor Analytics' },
    { id: 'predictions', label: 'AI Predictions' },
    { id: 'explainability', label: 'Explainable AI (SHAP)' },
    { id: 'anomalies', label: 'Anomaly Detection' },
    { id: 'investigation', label: 'Agent Investigation' },
    { id: 'maintenance', label: 'Work Orders & SOPs' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-subtle flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center font-mono font-bold text-lg border border-brand-500/20">
            {machine.code}
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">{machine.name}</h1>
              <StatusBadge status={machine.status} />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Type: <span className="font-semibold text-slate-700 dark:text-slate-300">{machine.type}</span> • Location:{' '}
              <span className="font-semibold text-slate-700 dark:text-slate-300">{machine.plant}</span> • Operating Hours:{' '}
              <span className="font-mono text-slate-700 dark:text-slate-300">{machine.operatingHours}h</span>
            </p>
          </div>
        </div>

        {/* Primary Actions */}
        <div className="flex items-center gap-2.5">
          <Link to={`/investigations`}>
            <Button size="md" variant="ai" leftIcon={<Sparkles className="w-4 h-4" />}>
              Investigate with AI
            </Button>
          </Link>
          <Link to={`/work-orders`}>
            <Button size="md" variant="outline" leftIcon={<Wrench className="w-4 h-4" />}>
              Create Maintenance Ticket
            </Button>
          </Link>
        </div>
      </div>

      {/* 4 Score Highlights */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Health Score</span>
            <div className="mt-2">
              <HealthScore score={machine.healthScore} size="lg" />
            </div>
          </CardContent>
        </Card>

        <Card className={machine.riskScore > 70 ? 'border-rose-500/30 bg-rose-500/5' : ''}>
          <CardContent className="p-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Failure Risk</span>
            <div className="text-2xl font-bold font-mono text-rose-600 dark:text-rose-400 mt-2">
              {machine.riskScore}%
            </div>
            <span className="text-[11px] text-rose-500 font-semibold uppercase">High Probability</span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Remaining Useful Life (RUL)</span>
            <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100 mt-2">
              {machine.rulHours} Hours
            </div>
            <span className="text-[11px] text-slate-400">Degradation estimate</span>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Anomaly Severity</span>
            <div className="text-2xl font-bold font-mono text-violet-600 dark:text-violet-400 mt-2">
              {machine.anomalyScore.toFixed(2)}
            </div>
            <span className="text-[11px] text-violet-500 font-semibold uppercase">Harmonic Vibration Spike</span>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-2 overflow-x-auto text-xs font-semibold">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-4 py-2.5 border-b-2 transition-colors whitespace-nowrap ${
              activeTab === t.id
                ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Live Sensor Gauge Cards */}
          <Card>
            <CardHeader>
              <CardTitle>Live Operating Envelope Telemetry</CardTitle>
              <span className="text-xs text-emerald-500 font-medium">● 100 Hz Ingestion</span>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Vibration (RMS)</span>
                  <div className="text-lg font-bold font-mono text-rose-500 mt-1">{machine.sensors.vibration} mm/s</div>
                  <span className="text-[10px] text-rose-500 font-semibold">Limit: &lt;3.5 mm/s (CRITICAL)</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Drive Temperature</span>
                  <div className="text-lg font-bold font-mono text-rose-500 mt-1">{machine.sensors.temperature} °C</div>
                  <span className="text-[10px] text-rose-500 font-semibold">Limit: &lt;65.0 °C (WARNING)</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Hydraulic Pressure</span>
                  <div className="text-lg font-bold font-mono text-emerald-500 mt-1">{machine.sensors.pressure} PSI</div>
                  <span className="text-[10px] text-slate-400 font-semibold">Nominal 100 PSI</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Motor RPM</span>
                  <div className="text-lg font-bold font-mono text-slate-900 dark:text-slate-100 mt-1">{machine.sensors.rpm} RPM</div>
                  <span className="text-[10px] text-slate-400 font-semibold">Rated 1800 RPM</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Stator Current</span>
                  <div className="text-lg font-bold font-mono text-amber-500 mt-1">{machine.sensors.current} A</div>
                  <span className="text-[10px] text-amber-500 font-semibold">Phase torque surge</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium">Active Power</span>
                  <div className="text-lg font-bold font-mono text-slate-900 dark:text-slate-100 mt-1">{machine.sensors.power} kW</div>
                  <span className="text-[10px] text-slate-400 font-semibold">415V 3-Phase</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Diagnostic Summary */}
          <Card className="border-brand-500/30 bg-brand-500/5">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-violet-500" />
                <CardTitle>Autonomous AI Diagnostic Summary</CardTitle>
              </div>
              <StatusBadge status="CRITICAL" size="sm" />
            </CardHeader>
            <CardContent className="p-5 space-y-4 text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              <p>
                <strong className="text-slate-900 dark:text-slate-100">Primary Diagnosed Failure: </strong>
                Bearing Wear / Shaft Misalignment (SKF-6205 drive bearing raceway spalling).
              </p>
              <p>
                <strong className="text-slate-900 dark:text-slate-100">Root Cause Hypothesis: </strong>
                Radial vibration harmonic amplitude of 4.25 mm/s exceeds the ISO 10816 threshold (3.5 mm/s). Combined with a drive temperature of 78.4°C (+28% above nominal baseline), the model projects mechanical bearing breakdown within <strong className="text-rose-500">143 operating hours</strong>.
              </p>
              <div className="p-3 rounded-lg bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 space-y-2">
                <span className="font-semibold text-slate-900 dark:text-slate-100">Recommended Next Action:</span>
                <p className="text-slate-600 dark:text-slate-400">
                  Stage emergency replacement of 2x SKF-6205 ball bearings and apply Mobilux EP2 lithium complex grease. Mandatory Lock-Out / Tag-Out (LOTO) isolation required before teardown.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB CONTENT 2: TELEMETRY TRENDS */}
      {activeTab === 'telemetry' && (
        <Card>
          <CardHeader>
            <CardTitle>Continuous Telemetry Curves (Vibration & Temperature)</CardTitle>
            <span className="text-xs text-slate-400">Last 1 Hour (10-minute intervals)</span>
          </CardHeader>
          <CardContent className="p-5">
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsLine data={SENSOR_TREND_DATA}>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#0d131f', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }} />
                  <Line type="monotone" dataKey="vibration" stroke="#ef4444" strokeWidth={2.5} name="Vibration (mm/s)" />
                  <Line type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} name="Temperature (°C)" />
                  <Line type="monotone" dataKey="current" stroke="#3b82f6" strokeWidth={1.5} name="Current (A)" />
                </RechartsLine>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* TAB CONTENT 3: EXPLAINABILITY (SHAP) */}
      {activeTab === 'explainability' && (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Why is this machine predicted to fail? (SHAP Factor Attribution)</CardTitle>
              <p className="text-xs text-slate-400 mt-0.5">Feature contribution to 87% failure probability score</p>
            </div>
          </CardHeader>
          <CardContent className="p-5 space-y-4">
            <div className="space-y-3">
              {MOCK_SHAP_FACTORS.map((factor) => (
                <div key={factor.feature} className="space-y-1 text-xs">
                  <div className="flex justify-between font-medium">
                    <span className="text-slate-800 dark:text-slate-200 font-semibold">{factor.feature}</span>
                    <span className="font-mono text-rose-500 font-bold">+{factor.impact}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 dark:bg-navy-950 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-amber-500 to-rose-500 rounded-full" style={{ width: `${factor.impact * 2.5}%` }} />
                  </div>
                  <p className="text-[11px] text-slate-400">{factor.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* TAB CONTENT 4: INVESTIGATION TIMELINE */}
      {activeTab === 'investigation' && (
        <Card>
          <CardHeader>
            <CardTitle>Multi-Agent Collaborative Diagnostic Timeline</CardTitle>
            <StatusBadge status="INVESTIGATION COMPLETE" size="sm" />
          </CardHeader>
          <CardContent className="p-5">
            <div className="relative border-l-2 border-slate-200 dark:border-slate-800 ml-4 space-y-6">
              {MOCK_INVESTIGATION_TIMELINE.map((item, idx) => (
                <div key={idx} className="relative pl-6">
                  <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-brand-500 ring-4 ring-white dark:ring-navy-900" />
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100">{item.step}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-brand-600 dark:text-brand-400 font-semibold">
                      {item.agent}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">{item.time}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">{item.detail}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* TAB CONTENT 5: WORK ORDERS */}
      {activeTab === 'maintenance' && (
        <Card>
          <CardHeader>
            <CardTitle>Staged Work Order & Safety Verification</CardTitle>
            <span className="text-xs font-mono text-amber-500 font-bold">AWAITING APPROVAL</span>
          </CardHeader>
          <CardContent className="p-5 space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-navy-900 border border-slate-200 dark:border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">WO-M1047-01: Emergency Bearing Replacement</span>
                <StatusBadge status="EMERGENCY" size="sm" />
              </div>
              <p className="text-slate-600 dark:text-slate-300">
                <strong>Assigned Technician: </strong>Alex Chen • <strong>Estimated MTTR: </strong>2.5 Hours
              </p>
              <div>
                <strong>Required Replacement Parts:</strong>
                <ul className="list-disc list-inside mt-1 text-slate-600 dark:text-slate-400 space-y-0.5">
                  <li>SKF-6205-2RSH Deep Groove Ball Bearing (Qty 2) - In Stock (Warehouse Bin A-12)</li>
                  <li>Mobilux EP2 Lithium Complex Industrial Grease (Qty 1 Cartridge)</li>
                </ul>
              </div>
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex gap-2">
                <Button size="sm" variant="danger">Approve Work Order (HITL Gate)</Button>
                <Button size="sm" variant="outline">Reject</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
