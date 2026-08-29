import React from 'react';
import { cn } from '../../utils/cn';

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => {
  return (
    <div
      className={cn('animate-pulse bg-slate-200 dark:bg-slate-800/80 rounded-md', className)}
      {...props}
    />
  );
};
