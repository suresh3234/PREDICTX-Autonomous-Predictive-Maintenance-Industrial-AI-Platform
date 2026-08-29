import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  Activity,
  Zap,
  AlertTriangle,
  Flame,
  Wrench,
  FileSpreadsheet,
  History,
  Bot,
  BookOpen,
  Search,
  Sparkles,
  Layers,
  FlaskConical,
  LineChart,
  GitPullRequest,
  RefreshCw,
  Users2,
  Boxes,
  ShieldCheck,
  BarChart3,
  UserCheck,
  ShieldAlert,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'OVERVIEW',
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'MONITORING',
    items: [
      { name: 'Machines', href: '/machines', icon: Cpu },
      { name: 'Live Telemetry', href: '/live-telemetry', icon: Activity, badge: 'LIVE' },
      { name: 'Predictions', href: '/predictions', icon: Zap },
      { name: 'Alerts', href: '/alerts', icon: AlertTriangle, badge: '5' },
      { name: 'Incidents', href: '/incidents', icon: Flame },
    ],
  },
  {
    title: 'MAINTENANCE',
    items: [
      { name: 'Maintenance', href: '/maintenance', icon: Wrench },
      { name: 'Work Orders', href: '/work-orders', icon: FileSpreadsheet },
      { name: 'Maintenance History', href: '/maintenance-history', icon: History },
    ],
  },
  {
    title: 'AI & INTELLIGENCE',
    items: [
      { name: 'AI Investigations', href: '/investigations', icon: Bot },
      { name: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
      { name: 'RAG Search', href: '/rag-search', icon: Search },
      { name: 'AI Assistant', href: '/assistant', icon: Sparkles },
    ],
  },
  {
    title: 'ML PLATFORM',
    items: [
      { name: 'Models', href: '/models', icon: Layers },
      { name: 'Experiments', href: '/experiments', icon: FlaskConical },
      { name: 'Model Monitoring', href: '/model-monitoring', icon: LineChart },
      { name: 'Drift Detection', href: '/drift-detection', icon: GitPullRequest },
      { name: 'Retraining', href: '/retraining', icon: RefreshCw },
    ],
  },
  {
    title: 'OPERATIONS',
    items: [
      { name: 'Agents', href: '/agents', icon: Users2 },
      { name: 'MCP Tools', href: '/mcp', icon: Boxes },
      { name: 'Evaluations', href: '/evaluations', icon: ShieldCheck },
      { name: 'Observability', href: '/observability', icon: BarChart3 },
    ],
  },
  {
    title: 'ADMINISTRATION',
    items: [
      { name: 'Users', href: '/users', icon: UserCheck },
      { name: 'Roles & Permissions', href: '/roles', icon: ShieldAlert },
      { name: 'Audit Logs', href: '/audit-logs', icon: FileText },
      { name: 'Settings', href: '/settings', icon: Settings },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        'h-screen sticky top-0 bg-white dark:bg-navy-900 border-r border-slate-200 dark:border-slate-800/80 flex flex-col transition-all duration-200 z-30 select-none',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
        {!collapsed ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white shadow-glow-primary font-bold text-base">
              P
            </div>
            <div>
              <div className="text-sm font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                PREDICTX
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-brand-500/10 text-brand-600 dark:text-brand-400 font-semibold border border-brand-500/20">
                  AI
                </span>
              </div>
              <p className="text-[10px] font-medium tracking-wider text-slate-400 uppercase">Failure Intelligence</p>
            </div>
          </div>
        ) : (
          <div className="mx-auto w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white shadow-glow-primary font-bold text-base">
            P
          </div>
        )}

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
                {section.title}
              </h4>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname.startsWith(item.href);

                return (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    title={collapsed ? item.name : undefined}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-colors group relative',
                      isActive
                        ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/40 dark:text-brand-300 font-semibold'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                    )}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-brand-500 rounded-r-full" />
                    )}
                    <Icon className={cn('w-4 h-4 flex-shrink-0', isActive ? 'text-brand-600 dark:text-brand-400' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300')} />
                    {!collapsed && <span className="truncate">{item.name}</span>}
                    {!collapsed && item.badge && (
                      <span
                        className={cn(
                          'ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded-full font-bold',
                          item.badge === 'LIVE'
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 animate-pulse border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                        )}
                      >
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Operator Badge */}
      <div className="p-3 border-t border-slate-100 dark:border-slate-800/80">
        {!collapsed ? (
          <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-navy-950/60 border border-slate-200/60 dark:border-slate-800 flex items-center gap-2.5">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <div className="text-[11px] truncate">
              <p className="font-semibold text-slate-800 dark:text-slate-200">Plant-01 Alpha</p>
              <p className="text-[10px] text-slate-400">Stream Connected</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center" title="Plant-01 Alpha: Stream Connected">
            <Radio className="w-4 h-4 text-emerald-500 animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
};
