import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Crown,
  Wrench,
  Cpu,
  Eye,
  CheckCircle2,
  XCircle,
  KeyRound,
  Lock,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  Zap,
  RefreshCw,
  Sliders,
} from 'lucide-react';
import { useAuth, DEMO_PRESETS, UserRole, ROLE_HIERARCHY } from '../contexts/AuthContext';
import { cn } from '../utils/cn';

interface ActionItem {
  id: string;
  name: string;
  category: string;
  minRole: UserRole;
  description: string;
}

const SYSTEM_ACTIONS: ActionItem[] = [
  {
    id: 'view_telemetry',
    name: 'View Real-Time Fleet Telemetry',
    category: 'Monitoring',
    minRole: 'VIEWER',
    description: 'Inspect live sensor streams, RPM, vibration, and temperature distributions.',
  },
  {
    id: 'view_health_metrics',
    name: 'Browse Machine Health Status',
    category: 'Monitoring',
    minRole: 'VIEWER',
    description: 'Access fleet overview cards and operational availability indexes.',
  },
  {
    id: 'direct_predict',
    name: 'Execute Real-Time ML Inference',
    category: 'Intelligence',
    minRole: 'OPERATOR',
    description: 'Calculate multi-model anomaly severity, failure probability, and RUL.',
  },
  {
    id: 'query_copilot',
    name: 'Query Reliability AI Copilot',
    category: 'Intelligence',
    minRole: 'OPERATOR',
    description: 'Conduct grounded natural language diagnostic conversations on equipment.',
  },
  {
    id: 'execute_mcp',
    name: 'Trigger MCP Tool Actions',
    category: 'Operations',
    minRole: 'OPERATOR',
    description: 'Call JSON-RPC Model Context Protocol tools for sensor probes & alarms.',
  },
  {
    id: 'approve_work_order',
    name: 'Approve Tier-2 HITL Maintenance',
    category: 'Safety & HITL',
    minRole: 'ENGINEER',
    description: 'Validate diagnostic reports and authoritatively dispatch maintenance work orders.',
  },
  {
    id: 'trigger_retrain',
    name: 'Trigger Automated Model Retraining',
    category: 'MLOps',
    minRole: 'ENGINEER',
    description: 'Initiate continuous retraining pipeline upon Kolmogorov-Smirnov drift detection.',
  },
  {
    id: 'emergency_shutdown',
    name: 'Execute Emergency Shutdown Approval',
    category: 'Safety & HITL',
    minRole: 'ADMIN',
    description: 'Authorize high-risk plant safety interlocks and emergency equipment halts.',
  },
  {
    id: 'audit_forensics',
    name: 'Export SHA-256 Chained Audit Trail',
    category: 'Governance',
    minRole: 'ADMIN',
    description: 'Inspect and cryptographically verify immutable sequential decision ledger.',
  },
];

export const RolesAndPermissions: React.FC = () => {
  const { user, switchRole, hasRole, openLoginModal, isLoading } = useAuth();
  const [selectedAction, setSelectedAction] = useState<ActionItem | null>(null);

  const getRoleCardStyle = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return 'border-purple-500/40 bg-purple-500/5 text-purple-600 dark:text-purple-300';
      case 'ENGINEER':
        return 'border-blue-500/40 bg-blue-500/5 text-blue-600 dark:text-blue-300';
      case 'OPERATOR':
        return 'border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-300';
      case 'VIEWER':
        return 'border-slate-400/40 bg-slate-500/5 text-slate-600 dark:text-slate-300';
    }
  };

  const getRoleIcon = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return Crown;
      case 'ENGINEER':
        return Wrench;
      case 'OPERATOR':
        return Cpu;
      case 'VIEWER':
        return Eye;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
            <ShieldAlert className="w-7 h-7 text-brand-500" />
            Security & Role-Based Access Control (RBAC)
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Hierarchical authorization matrix enforcing zero-trust industrial safety policies with JWT Bearer tokens.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={openLoginModal}
            className="px-3.5 py-2 text-xs font-semibold rounded-xl bg-brand-600 hover:bg-brand-500 text-white shadow-subtle flex items-center gap-2 transition-all"
          >
            <KeyRound className="w-4 h-4" />
            <span>Switch Identity / Token</span>
          </button>
        </div>
      </div>

      {/* Active Session Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-navy-900 to-slate-900 text-white border border-slate-800 shadow-elevated relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-brand-500/10 blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-glow-primary border border-white/20">
              {user?.name ? user.name.slice(0, 2).toUpperCase() : 'PX'}
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h3 className="text-base font-bold text-white">{user?.name || user?.username}</h3>
                <span className={cn('text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border', 
                  user?.role === 'ADMIN' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
                  user?.role === 'ENGINEER' ? 'bg-blue-500/20 text-blue-300 border-blue-500/40' :
                  user?.role === 'OPERATOR' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                  'bg-slate-500/20 text-slate-300 border-slate-500/40'
                )}>
                  LEVEL {ROLE_HIERARCHY[user?.role || 'VIEWER']} • {user?.role}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{user?.title || 'Certified Industrial User'}</p>
              <p className="text-[10px] font-mono text-slate-400 mt-1 flex items-center gap-2">
                <span>Principal: <strong className="text-slate-200">{user?.username}</strong></span>
                <span>•</span>
                <span>Algorithm: <strong className="text-slate-200">HMAC-SHA256</strong></span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {(['VIEWER', 'OPERATOR', 'ENGINEER', 'ADMIN'] as UserRole[]).map((r) => (
              <button
                key={r}
                onClick={() => switchRole(r)}
                disabled={isLoading}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5',
                  user?.role === r
                    ? 'bg-white text-slate-900 shadow-md font-bold'
                    : 'bg-white/10 hover:bg-white/20 text-white/80'
                )}
              >
                <span>{r}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 4-Tier Hierarchy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {(['VIEWER', 'OPERATOR', 'ENGINEER', 'ADMIN'] as UserRole[]).map((role) => {
          const preset = DEMO_PRESETS[role];
          const Icon = getRoleIcon(role);
          const isCurrent = user?.role === role;
          const level = ROLE_HIERARCHY[role];

          return (
            <div
              key={role}
              className={cn(
                'p-5 rounded-2xl border transition-all duration-200 flex flex-col justify-between',
                getRoleCardStyle(role),
                isCurrent && 'ring-2 ring-brand-500 shadow-glow-subtle'
              )}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 font-bold text-sm">
                    <Icon className="w-5 h-5" />
                    <span>{role}</span>
                  </div>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-white/10 border border-current">
                    Tier {level}
                  </span>
                </div>
                <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{preset.name}</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mb-4 line-clamp-2">{preset.title}</p>
              </div>

              <div className="pt-3 border-t border-slate-200/40 dark:border-slate-800/80 flex items-center justify-between">
                <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">
                  {level === 1 && 'Read-only telemetry'}
                  {level === 2 && 'Inference & Copilot'}
                  {level === 3 && 'HITL Approvals & Retrain'}
                  {level === 4 && 'Full Forensic & Shutdown'}
                </span>
                {isCurrent ? (
                  <span className="text-[10px] font-bold text-brand-600 dark:text-brand-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> ACTIVE
                  </span>
                ) : (
                  <button
                    onClick={() => switchRole(role)}
                    className="text-[10px] font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 flex items-center gap-1"
                  >
                    Switch <ArrowRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive Authorization Simulator Matrix */}
      <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-brand-500" />
              Live Permission Evaluation Matrix
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Evaluated against your active JWT session ({user?.role || 'VIEWER'}).
            </p>
          </div>
          <span className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20 font-semibold">
            Active Security Policy: ZERO_TRUST_v2.4
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-[11px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 dark:bg-navy-950/60 border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th className="py-3 px-4">Action & Operational Scope</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Min. Required Role</th>
                <th className="py-3 px-4">Access for {user?.role || 'VIEWER'}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
              {SYSTEM_ACTIONS.map((action) => {
                const allowed = hasRole(action.minRole);
                const reqLevel = ROLE_HIERARCHY[action.minRole];

                return (
                  <tr key={action.id} className="hover:bg-slate-50/60 dark:hover:bg-navy-850/50 transition-colors">
                    <td className="py-3.5 px-4">
                      <p className="font-semibold text-slate-900 dark:text-slate-100">{action.name}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">{action.description}</p>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono text-[10px]">
                        {action.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={cn('px-2 py-0.5 rounded font-mono font-bold text-[10px] border',
                        action.minRole === 'ADMIN' ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20' :
                        action.minRole === 'ENGINEER' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20' :
                        action.minRole === 'OPERATOR' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' :
                        'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20'
                      )}>
                        Tier {reqLevel}: {action.minRole}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {allowed ? (
                        <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-bold">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>GRANTED</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-rose-500 dark:text-rose-400 font-semibold">
                          <XCircle className="w-4 h-4" />
                          <span>BLOCKED (Insufficient Rank)</span>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
