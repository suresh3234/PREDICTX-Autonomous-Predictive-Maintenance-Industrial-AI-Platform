import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, ArrowUpDown, Bot, Plus, Download, Wrench } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { HealthScore } from '../components/ui/HealthScore';
import { Button } from '../components/ui/Button';
import { MOCK_MACHINES } from '../api/mockData';

export const Machines: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredMachines = MOCK_MACHINES.filter((m) => {
    const matchesSearch =
      m.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.plant.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'ALL' || m.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Industrial Machine Fleet
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time operating envelopes, Remaining Useful Life (RUL), and predictive failure probabilities.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" leftIcon={<Download className="w-3.5 h-3.5" />}>
            Export CSV
          </Button>
          <Button size="sm" variant="primary" leftIcon={<Plus className="w-3.5 h-3.5" />}>
            Register Machine
          </Button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 p-4 bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 rounded-xl">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by ID, name, equipment type, plant..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto">
          {['ALL', 'CRITICAL', 'WARNING', 'HEALTHY'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
                statusFilter === s
                  ? 'bg-brand-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Machines Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-navy-900 text-slate-400 border-b border-slate-100 dark:border-slate-800 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3.5">Machine ID</th>
                  <th className="px-5 py-3.5">Type & Location</th>
                  <th className="px-5 py-3.5">Health Score</th>
                  <th className="px-5 py-3.5">Failure Probability</th>
                  <th className="px-5 py-3.5">RUL</th>
                  <th className="px-5 py-3.5">Anomaly Score</th>
                  <th className="px-5 py-3.5">Last Service</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredMachines.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-4">
                      <Link to={`/machines/${m.code}`} className="font-mono font-bold text-brand-600 dark:text-brand-400 hover:underline">
                        {m.code}
                      </Link>
                      <div className="text-[11px] text-slate-400 truncate max-w-xs">{m.name}</div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{m.type}</span>
                      <div className="text-[11px] text-slate-400">{m.plant}</div>
                    </td>
                    <td className="px-5 py-4">
                      <HealthScore score={m.healthScore} size="sm" />
                    </td>
                    <td className="px-5 py-4 font-mono font-semibold">
                      <span className={m.failureProbability > 0.7 ? 'text-rose-500 font-bold' : m.failureProbability > 0.3 ? 'text-amber-500' : 'text-emerald-500'}>
                        {(m.failureProbability * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-5 py-4 font-mono font-medium text-slate-700 dark:text-slate-300">
                      {m.rulHours}h
                    </td>
                    <td className="px-5 py-4 font-mono text-slate-700 dark:text-slate-300">
                      {m.anomalyScore.toFixed(2)}
                    </td>
                    <td className="px-5 py-4 text-slate-500">{m.lastMaintenance}</td>
                    <td className="px-5 py-4">
                      <StatusBadge status={m.status} size="sm" />
                    </td>
                    <td className="px-5 py-4 text-right space-x-2">
                      <Link to={`/machines/${m.code}`}>
                        <Button size="sm" variant="ai" leftIcon={<Bot className="w-3.5 h-3.5" />}>
                          Inspect
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
