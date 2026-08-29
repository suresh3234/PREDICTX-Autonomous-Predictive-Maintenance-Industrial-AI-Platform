import React, { useState } from 'react';
import { Bot, CheckCircle2, Cpu, Flame, Layers, Search, Sparkles, Wrench } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { MOCK_INVESTIGATION_TIMELINE } from '../api/mockData';

export const Investigations: React.FC = () => {
  const [selectedMachine, setSelectedMachine] = useState('M1047');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Autonomous AI Investigations
            </h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-violet-500/10 text-violet-600 dark:text-violet-400 border border-violet-500/20">
              <Sparkles className="w-3.5 h-3.5" /> 5 Multi-Agent Fleet Active
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Supervisor, Investigator, Root Cause, Knowledge, and Maintenance Verification Agent execution audit.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="ai" leftIcon={<Sparkles className="w-3.5 h-3.5" />}>
            New Autonomous Investigation
          </Button>
        </div>
      </div>

      {/* Investigation Details Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Active Incidents */}
        <Card>
          <CardHeader>
            <CardTitle>Active Incident Queue</CardTitle>
            <span className="text-xs font-mono text-rose-500 font-bold">2 INCIDENTS</span>
          </CardHeader>
          <CardContent className="p-3 space-y-2">
            <div
              onClick={() => setSelectedMachine('M1047')}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                selectedMachine === 'M1047'
                  ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/30'
                  : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="font-mono text-slate-900 dark:text-slate-100">INC-204 • M1047</span>
                <StatusBadge status="CRITICAL" size="sm" />
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 font-medium mt-1">
                Bearing raceway spalling & harmonic vibration surge
              </p>
              <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                <span>RUL: 143h</span>
                <span className="font-mono text-emerald-500 font-semibold">6 Agents Consulted</span>
              </div>
            </div>

            <div
              onClick={() => setSelectedMachine('M4120')}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                selectedMachine === 'M4120'
                  ? 'border-brand-500 bg-brand-50/40 dark:bg-brand-950/30'
                  : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="font-mono text-slate-900 dark:text-slate-100">INC-205 • M4120</span>
                <StatusBadge status="HIGH" size="sm" />
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-300 font-medium mt-1">
                Coolant loop delta temperature breach (88.6°C)
              </p>
              <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                <span>RUL: 210h</span>
                <span className="font-mono text-emerald-500 font-semibold">6 Agents Consulted</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right: Step-by-Step Multi-Agent Execution Audit */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div>
                <CardTitle>Autonomous Multi-Agent Investigation Audit ({selectedMachine})</CardTitle>
                <p className="text-xs text-slate-400 mt-0.5">End-to-end evidence retrieval, RAG grounding, and work order generation</p>
              </div>
              <StatusBadge status="RESOLVED & VERIFIED" size="sm" />
            </div>
          </CardHeader>
          <CardContent className="p-5">
            <div className="relative border-l-2 border-slate-200 dark:border-slate-800 ml-4 space-y-6">
              {MOCK_INVESTIGATION_TIMELINE.map((item, idx) => (
                <div key={idx} className="relative pl-6">
                  <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-violet-500 ring-4 ring-white dark:ring-navy-900" />
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100">{item.step}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/10 text-violet-600 dark:text-violet-400 font-bold border border-violet-500/20">
                      {item.agent}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">{item.time}</span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">{item.detail}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
