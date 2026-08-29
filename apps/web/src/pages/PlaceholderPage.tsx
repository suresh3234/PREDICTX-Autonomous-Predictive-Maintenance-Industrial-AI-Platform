import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { LucideIcon, Sparkles } from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  subtitle: string;
  badge?: string;
  icon?: LucideIcon;
  section: string;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  subtitle,
  badge = 'FOUNDATION READY',
  icon: Icon = Sparkles,
  section,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">{title}</h1>
            <StatusBadge status={badge} size="sm" pulse={false} />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline">Export Telemetry</Button>
          <Button size="sm" variant="ai" leftIcon={<Icon className="w-3.5 h-3.5" />}>
            Run AI Audit
          </Button>
        </div>
      </div>

      {/* Foundation Architecture Card */}
      <Card>
        <CardHeader>
          <CardTitle>Architecture Status • {section}</CardTitle>
          <span className="text-xs font-mono text-brand-600 dark:text-brand-400 font-semibold">
            PHASE 1 COMPLETE
          </span>
        </CardHeader>
        <CardContent>
          <div className="p-6 rounded-xl bg-slate-50 dark:bg-navy-900/50 border border-slate-200/60 dark:border-slate-800 text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-brand-500/10 text-brand-500 mx-auto flex items-center justify-center">
              <Icon className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              {title} Module Initialized
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              This route is fully wired into the PredictX Design System, Theme Engine, and Command Palette router. Dedicated operational views will render in sequential curriculum phases.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
