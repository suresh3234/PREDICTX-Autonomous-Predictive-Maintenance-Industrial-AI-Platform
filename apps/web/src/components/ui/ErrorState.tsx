import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../utils/cn';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load operational data',
  message,
  onRetry,
  className,
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center p-6 text-center rounded-xl border border-rose-200 dark:border-rose-950/60 bg-rose-50/30 dark:bg-rose-950/10', className)}>
      <div className="p-2.5 rounded-full bg-rose-100 dark:bg-rose-900/40 text-rose-600 dark:text-rose-400 mb-3">
        <AlertTriangle className="w-5 h-5" />
      </div>
      <h4 className="text-sm font-semibold text-rose-900 dark:text-rose-200 mb-1">{title}</h4>
      <p className="text-xs text-rose-600 dark:text-rose-400 max-w-sm mb-4">{message}</p>
      {onRetry && (
        <Button size="sm" variant="danger" leftIcon={<RefreshCw className="w-3.5 h-3.5" />} onClick={onRetry}>
          Retry Connection
        </Button>
      )}
    </div>
  );
};
