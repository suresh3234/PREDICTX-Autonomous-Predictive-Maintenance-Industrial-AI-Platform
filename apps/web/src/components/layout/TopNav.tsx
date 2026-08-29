import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import {
  Search,
  Moon,
  Sun,
  Bell,
  CheckCircle2,
  ChevronDown,
  HelpCircle,
  Activity,
  Cpu,
  Layers,
  Sparkles,
  Database,
  ShieldCheck,
  LogOut,
  User,
  KeyRound,
  Crown,
  Wrench,
  Eye,
} from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth, UserRole } from '../../contexts/AuthContext';
import { cn } from '../../utils/cn';

interface TopNavProps {
  onOpenCommandPalette: () => void;
  onOpenAssistant: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  onOpenCommandPalette,
  onOpenAssistant,
}) => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { user, openLoginModal, logout, switchRole } = useAuth();
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Generate dynamic breadcrumbs
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const breadcrumbs = [
    { label: 'PredictX', href: '/dashboard' },
    ...pathSegments.map((seg, idx) => ({
      label: seg.charAt(0).toUpperCase() + seg.slice(1).replace('-', ' '),
      href: '/' + pathSegments.slice(0, idx + 1).join('/'),
    })),
  ];

  const getRoleBadgeColor = (role?: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20';
      case 'ENGINEER':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      case 'OPERATOR':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
      default:
        return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
    }
  };

  const getUserInitials = (name?: string, username?: string) => {
    if (name) {
      const parts = name.split(' ');
      if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
      return name.slice(0, 2).toUpperCase();
    }
    return (username || 'PX').slice(0, 2).toUpperCase();
  };

  return (
    <header className="h-16 bg-white/80 dark:bg-navy-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800/80 sticky top-0 z-20 px-6 flex items-center justify-between">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb.href}>
            {idx > 0 && <span className="text-slate-300 dark:text-slate-600">/</span>}
            {idx === breadcrumbs.length - 1 ? (
              <span className="text-slate-900 dark:text-slate-100 font-semibold">{crumb.label}</span>
            ) : (
              <Link to={crumb.href} className="hover:text-slate-900 dark:hover:text-slate-200 transition-colors">
                {crumb.label}
              </Link>
            )}
          </React.Fragment>
        ))}
      </nav>

      {/* Global Search Bar (Command Palette Trigger) */}
      <button
        onClick={onOpenCommandPalette}
        className="hidden md:flex items-center gap-3 px-3.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-navy-950/60 text-slate-400 hover:border-slate-300 dark:hover:border-slate-700 text-xs transition-colors w-72"
      >
        <Search className="w-4 h-4 text-slate-400" />
        <span className="flex-1 text-left">Search machines, alerts, SOPs...</span>
        <kbd className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-300 dark:border-slate-700">
          Ctrl K
        </kbd>
      </button>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* AI Assistant Quick Trigger */}
        <button
          onClick={onOpenAssistant}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-600/10 to-indigo-600/10 hover:from-violet-600/20 hover:to-indigo-600/20 text-violet-700 dark:text-violet-300 border border-violet-500/20 text-xs font-semibold shadow-subtle transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-violet-500 animate-pulse" />
          <span className="hidden sm:inline">Ask AI Copilot</span>
        </button>

        {/* System Status Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowStatusMenu(!showStatusMenu);
              setShowUserMenu(false);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20 text-xs font-medium hover:bg-emerald-500/15 transition-colors"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="hidden sm:inline">Systems Operational</span>
            <ChevronDown className="w-3 h-3 opacity-70" />
          </button>

          {showStatusMenu && (
            <div className="absolute right-0 mt-2 w-64 p-3 bg-white dark:bg-navy-850 rounded-xl shadow-elevated border border-slate-200 dark:border-slate-800 text-xs space-y-2 z-50 animate-fade-in">
              <p className="font-semibold text-slate-900 dark:text-slate-100 pb-1 border-b border-slate-100 dark:border-slate-800">
                Core Service Health
              </p>
              <div className="space-y-1.5 text-slate-600 dark:text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-emerald-500" /> REST API Gateway</span>
                  <span className="text-emerald-500 font-mono font-medium">99.9% (12ms)</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-emerald-500" /> ML Inference Pipeline</span>
                  <span className="text-emerald-500 font-mono font-medium">45ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-emerald-500" /> Kafka Streaming Broker</span>
                  <span className="text-emerald-500 font-mono font-medium">0 lag</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-emerald-500" /> PostgreSQL & RAG</span>
                  <span className="text-emerald-500 font-mono font-medium">Healthy</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Notifications Icon */}
        <button
          className="relative p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500" />
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* User Profile & RBAC Dropdown */}
        <div className="relative pl-2 border-l border-slate-200 dark:border-slate-800">
          <button
            onClick={() => {
              setShowUserMenu(!showUserMenu);
              setShowStatusMenu(false);
            }}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
          >
            <div className="w-8 h-8 rounded-full bg-brand-600 text-white font-bold text-xs flex items-center justify-center border-2 border-brand-500/30 shadow-subtle">
              {getUserInitials(user?.name, user?.username)}
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-bold text-slate-800 dark:text-slate-100 truncate max-w-[110px]">
                {user?.name?.split(' ')[0] || user?.username || 'Guest'}
              </p>
              <span className={cn('text-[9px] font-mono font-bold px-1.5 py-0.2 rounded border', getRoleBadgeColor(user?.role))}>
                {user?.role || 'VIEWER'}
              </span>
            </div>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-72 p-3 bg-white dark:bg-navy-850 rounded-xl shadow-elevated border border-slate-200 dark:border-slate-800 text-xs space-y-3 z-50 animate-fade-in">
              <div className="pb-2 border-b border-slate-100 dark:border-slate-800">
                <p className="font-bold text-slate-900 dark:text-slate-100">{user?.name || user?.username}</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">{user?.title || 'Certified Operator'}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className={cn('text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border', getRoleBadgeColor(user?.role))}>
                    RBAC: {user?.role}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Principal: {user?.username}</span>
                </div>
              </div>

              {/* Fast Persona Switcher */}
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Fast RBAC Role Switch
                </p>
                <div className="grid grid-cols-2 gap-1.5">
                  <button
                    onClick={() => {
                      switchRole('ADMIN');
                      setShowUserMenu(false);
                    }}
                    className={cn(
                      'p-1.5 rounded-lg border text-left text-[11px] font-semibold flex items-center gap-1.5 transition-colors',
                      user?.role === 'ADMIN'
                        ? 'border-purple-500 bg-purple-500/10 text-purple-600 dark:text-purple-400'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    )}
                  >
                    <Crown className="w-3.5 h-3.5" /> Admin (L4)
                  </button>
                  <button
                    onClick={() => {
                      switchRole('ENGINEER');
                      setShowUserMenu(false);
                    }}
                    className={cn(
                      'p-1.5 rounded-lg border text-left text-[11px] font-semibold flex items-center gap-1.5 transition-colors',
                      user?.role === 'ENGINEER'
                        ? 'border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    )}
                  >
                    <Wrench className="w-3.5 h-3.5" /> Engineer (L3)
                  </button>
                  <button
                    onClick={() => {
                      switchRole('OPERATOR');
                      setShowUserMenu(false);
                    }}
                    className={cn(
                      'p-1.5 rounded-lg border text-left text-[11px] font-semibold flex items-center gap-1.5 transition-colors',
                      user?.role === 'OPERATOR'
                        ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    )}
                  >
                    <Cpu className="w-3.5 h-3.5" /> Operator (L2)
                  </button>
                  <button
                    onClick={() => {
                      switchRole('VIEWER');
                      setShowUserMenu(false);
                    }}
                    className={cn(
                      'p-1.5 rounded-lg border text-left text-[11px] font-semibold flex items-center gap-1.5 transition-colors',
                      user?.role === 'VIEWER'
                        ? 'border-slate-400 bg-slate-500/10 text-slate-700 dark:text-slate-300'
                        : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    )}
                  >
                    <Eye className="w-3.5 h-3.5" /> Viewer (L1)
                  </button>
                </div>
              </div>

              {/* Actions */}
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-1">
                <button
                  onClick={() => {
                    openLoginModal();
                    setShowUserMenu(false);
                  }}
                  className="w-full py-1.5 px-2 rounded-lg text-left font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-2 transition-colors"
                >
                  <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                  <span>Custom JWT Login...</span>
                </button>
                <Link
                  to="/roles"
                  onClick={() => setShowUserMenu(false)}
                  className="w-full py-1.5 px-2 rounded-lg text-left font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-2 transition-colors"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                  <span>Inspect RBAC Matrix</span>
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                  className="w-full py-1.5 px-2 rounded-lg text-left font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 flex items-center gap-2 transition-colors"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

