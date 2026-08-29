import React from 'react';
import { cn } from '../../utils/cn';

export type MachineStatus = 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'OFFLINE' | 'AI_ACTIVE' | 'RESOLVED' | 'PENDING';

interface StatusBadgeProps {
  status: MachineStatus | string;
  size?: 'sm' | 'md';
  pulse?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  pulse = true,
  className,
}) => {
  const normStatus = status.toUpperCase();

  const styles: Record<string, { bg: string; text: string; dot: string; border: string }> = {
    HEALTHY: {
      bg: 'bg-emerald-500/10 dark:bg-emerald-500/15',
      text: 'text-emerald-700 dark:text-emerald-400',
      dot: 'bg-emerald-500',
      border: 'border-emerald-500/20',
    },
    WARNING: {
      bg: 'bg-amber-500/10 dark:bg-amber-500/15',
      text: 'text-amber-700 dark:text-amber-400',
      dot: 'bg-amber-500',
      border: 'border-amber-500/20',
    },
    CRITICAL: {
      bg: 'bg-rose-500/10 dark:bg-rose-500/15',
      text: 'text-rose-700 dark:text-rose-400',
      dot: 'bg-rose-500',
      border: 'border-rose-500/20',
    },
    OFFLINE: {
      bg: 'bg-slate-500/10 dark:bg-slate-500/15',
      text: 'text-slate-600 dark:text-slate-400',
      dot: 'bg-slate-400',
      border: 'border-slate-500/20',
    },
    AI_ACTIVE: {
      bg: 'bg-violet-500/10 dark:bg-violet-500/15',
      text: 'text-violet-700 dark:text-violet-400',
      dot: 'bg-violet-500',
      border: 'border-violet-500/20',
    },
    RESOLVED: {
      bg: 'bg-blue-500/10 dark:bg-blue-500/15',
      text: 'text-blue-700 dark:text-blue-400',
      dot: 'bg-blue-500',
      border: 'border-blue-500/20',
    },
  };

  const current = styles[normStatus] || styles.OFFLINE;

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full border',
        size === 'sm' ? 'px-2 py-0.5 text-xs gap-1.5' : 'px-2.5 py-1 text-xs gap-2',
        current.bg,
        current.text,
        current.border,
        className
      )}
    >
      <span className="relative flex h-2 w-2">
        {pulse && normStatus === 'CRITICAL' && (
          <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', current.dot)} />
        )}
        <span className={cn('relative inline-flex rounded-full h-2 w-2', current.dot)} />
      </span>
      <span>{normStatus.replace('_', ' ')}</span>
    </span>
  );
};
