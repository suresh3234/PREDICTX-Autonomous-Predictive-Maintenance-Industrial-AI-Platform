import React, { useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  KeyRound,
  Lock,
  User,
  Check,
  AlertCircle,
  X,
  Sparkles,
  ArrowRight,
  Cpu,
  Wrench,
  Eye,
  Crown,
} from 'lucide-react';
import { useAuth, DEMO_PRESETS, UserRole } from '../../contexts/AuthContext';
import { cn } from '../../utils/cn';

export const LoginModal: React.FC = () => {
  const { user, isLoginModalOpen, closeLoginModal, login, switchRole, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState<'presets' | 'custom'>('presets');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isLoginModalOpen) return null;

  const handleCustomSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setErrorMsg('Please enter both username and password.');
      return;
    }
    setErrorMsg(null);
    try {
      await login(username, password);
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed. Please check credentials.');
    }
  };

  const handlePresetSelect = async (role: UserRole) => {
    setErrorMsg(null);
    try {
      await switchRole(role);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to authenticate preset user.');
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

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return 'border-purple-500/30 bg-purple-500/10 text-purple-600 dark:text-purple-400 hover:border-purple-500';
      case 'ENGINEER':
        return 'border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400 hover:border-blue-500';
      case 'OPERATOR':
        return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:border-emerald-500';
      case 'VIEWER':
        return 'border-slate-500/30 bg-slate-500/10 text-slate-600 dark:text-slate-400 hover:border-slate-500';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-xl bg-white dark:bg-navy-900 rounded-2xl shadow-elevated border border-slate-200 dark:border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800/80 flex items-start justify-between bg-gradient-to-r from-slate-50 via-white to-slate-50 dark:from-navy-950 dark:via-navy-900 dark:to-navy-950">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white shadow-glow-primary">
              <KeyRound className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                PredictX Security & Access Control
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold border border-emerald-500/20">
                  JWT HMAC-SHA256
                </span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Authenticate with plant credentials or switch persona to test RBAC tiers.
              </p>
            </div>
          </div>
          <button
            onClick={closeLoginModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-100 dark:border-slate-800 px-6 pt-3 gap-4">
          <button
            onClick={() => setActiveTab('presets')}
            className={cn(
              'pb-3 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5',
              activeTab === 'presets'
                ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
            )}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Instant Role Switcher
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={cn(
              'pb-3 text-xs font-semibold border-b-2 transition-all flex items-center gap-1.5',
              activeTab === 'custom'
                ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'
            )}
          >
            <Lock className="w-3.5 h-3.5" />
            Custom Credentials
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {activeTab === 'presets' ? (
            <div className="space-y-3">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Select a certified persona to test permissions and cryptographic signing:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {(Object.keys(DEMO_PRESETS) as UserRole[]).map((role) => {
                  const preset = DEMO_PRESETS[role];
                  const Icon = getRoleIcon(role);
                  const isCurrent = user?.role === role;

                  return (
                    <button
                      key={role}
                      onClick={() => handlePresetSelect(role)}
                      disabled={isLoading}
                      className={cn(
                        'p-3 rounded-xl border text-left transition-all relative group flex flex-col justify-between gap-2',
                        getRoleColor(role),
                        isCurrent && 'ring-2 ring-brand-500'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 font-bold text-xs">
                          <Icon className="w-4 h-4" />
                          <span>{role}</span>
                        </div>
                        {isCurrent ? (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-500 text-white flex items-center gap-1">
                            <Check className="w-3 h-3" /> ACTIVE
                          </span>
                        ) : (
                          <span className="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                            Switch <ArrowRight className="w-3 h-3" />
                          </span>
                        )}
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{preset.name}</p>
                        <p className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-1">{preset.title}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            <form onSubmit={handleCustomSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. admin, engineer, operator, viewer"
                    className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter account password"
                    className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition-colors shadow-subtle flex items-center justify-center gap-2 mt-2"
              >
                {isLoading ? 'Signing in...' : 'Authenticate & Issue JWT Token'}
              </button>
            </form>
          )}

          {/* Active Token Info */}
          {user && (
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-navy-950/80 border border-slate-200/80 dark:border-slate-800 text-[11px] space-y-1">
              <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 font-mono">
                <span>Active Principal: <strong className="text-slate-800 dark:text-slate-200">{user.username}</strong></span>
                <span className="px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-600 dark:text-brand-400 font-bold border border-brand-500/20">
                  Role: {user.role}
                </span>
              </div>
              <p className="text-slate-400 truncate font-mono text-[10px]">
                Token: {user.token.slice(0, 32)}...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
