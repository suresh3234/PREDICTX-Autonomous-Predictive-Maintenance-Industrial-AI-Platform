import React from 'react';
import { cn } from '../../utils/cn';

interface HealthScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const HealthScore: React.FC<HealthScoreProps> = ({
  score,
  size = 'md',
  showLabel = true,
  className,
}) => {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));

  let colorClass = 'text-emerald-500 stroke-emerald-500';
  let bgClass = 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
  let label = 'HEALTHY';

  if (clamped < 50) {
    colorClass = 'text-rose-500 stroke-rose-500';
    bgClass = 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20';
    label = 'CRITICAL';
  } else if (clamped < 80) {
    colorClass = 'text-amber-500 stroke-amber-500';
    bgClass = 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
    label = 'WARNING';
  }

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1 font-semibold',
    lg: 'text-2xl px-4 py-2 font-bold',
  };

  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <div className={cn('rounded-lg border font-mono flex items-center justify-center', bgClass, sizes[size])}>
        {clamped}
        <span className="text-[10px] opacity-70 ml-0.5">/100</span>
      </div>
      {showLabel && (
        <span className={cn('text-xs font-medium tracking-wide uppercase', colorClass)}>
          {label}
        </span>
      )}
    </div>
  );
};
