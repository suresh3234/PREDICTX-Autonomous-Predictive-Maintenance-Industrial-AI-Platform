import React, { useState, useEffect } from 'react';
import {
  Flame,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Search,
  Users,
  Wrench,
  ChevronRight,
} from 'lucide-react';
import { fetchIncidents } from '../api/client';

export const Incidents: React.FC = () => {
  const [incidents, setIncidents] = useState<any[]>([]);

  useEffect(() => {
    async function loadIncidents() {
      try {
        const res = await fetchIncidents();
        setIncidents(res.incidents || []);
      } catch (err) {
        console.error('Failed loading incidents:', err);
      }
    }
    loadIncidents();
  }, []);

  const sampleIncidents = [
    {
      incident_id: 'INC-M1003-4A82',
      machine_code: 'M1003',
      machine_type: 'Hydraulic Press',
      severity: 'CRITICAL',
      detected_at: '2026-08-29T11:42:00Z',
      failure_mode: 'Hydraulic Seal Rupture & Thermal Surge',
      status: 'INVESTIGATING',
      risk_probability: 89.4,
      assigned_agent: 'Supervisor Orchestrator',
      assigned_team: 'Hydraulics Unit A',
    },
    {
      incident_id: 'INC-M1002-9F12',
      machine_code: 'M1002',
      machine_type: 'Induction Motor',
      severity: 'HIGH',
      detected_at: '2026-08-29T09:15:00Z',
      failure_mode: 'Bearing Wear & Harmonic Vibration',
      status: 'WORK_ORDER_QUEUED',
      risk_probability: 68.0,
      assigned_agent: 'Maintenance Planner',
      assigned_team: 'Electrical Maintenance',
    },
    {
      incident_id: 'INC-M1001-3C77',
      machine_code: 'M1001',
      machine_type: 'Rotary Compressor',
      severity: 'WARNING',
      detected_at: '2026-08-28T18:30:00Z',
      failure_mode: 'Cooling Radiator Fin Clogging',
      status: 'RESOLVED',
      risk_probability: 38.5,
      assigned_agent: 'Verification Agent',
      assigned_team: 'Plant Services',
    },
  ];

  const list = incidents.length > 0 ? incidents : sampleIncidents;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Incident Management & Triage</h1>
            <p className="text-sm text-slate-400">
              End-to-end incident lifecycle from autonomous multi-agent anomaly detection to root cause resolution
            </p>
          </div>
        </div>
      </div>

      {/* Incident Cards */}
      <div className="space-y-4">
        {list.map((inc, idx) => (
          <div
            key={idx}
            className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3 hover:border-slate-700 transition-all"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-slate-950 text-indigo-400 border border-slate-800">
                  {inc.incident_id}
                </span>
                <span className="text-xs font-mono text-slate-300 font-semibold">{inc.machine_code} ({inc.machine_type})</span>
                <span
                  className={`px-2.5 py-0.5 rounded text-[11px] font-bold ${
                    inc.severity === 'CRITICAL'
                      ? 'bg-rose-500/20 text-rose-400'
                      : inc.severity === 'HIGH'
                      ? 'bg-orange-500/20 text-orange-400'
                      : 'bg-amber-500/20 text-amber-400'
                  }`}
                >
                  {inc.severity}
                </span>
              </div>

              <span
                className={`px-3 py-1 rounded-full text-xs font-bold ${
                  inc.status === 'INVESTIGATING'
                    ? 'bg-rose-500/20 text-rose-300 animate-pulse'
                    : inc.status === 'RESOLVED'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-indigo-500/20 text-indigo-300'
                }`}
              >
                {inc.status}
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-white mb-1">{inc.failure_mode}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-400 mt-2">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span>Detected: {new Date(inc.detected_at).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-teal-400" />
                  <span>Agent: <strong className="text-slate-200">{inc.assigned_agent}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-indigo-400" />
                  <span>Assigned: <strong className="text-slate-200">{inc.assigned_team}</strong></span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
