import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Bot, CheckCircle2, Filter, Flame, RefreshCw, Wrench } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';
import { MOCK_ALERTS } from '../api/mockData';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState(MOCK_ALERTS);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'ACKNOWLEDGED' } : a))
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Threat & Alert Center
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time threshold violations, ML anomaly triggers, and automated incident escalation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
            Acknowledge All
          </Button>
        </div>
      </div>

      {/* Alert Feed List */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <Card key={alert.id} className={alert.severity === 'CRITICAL' ? 'border-rose-500/40 bg-rose-500/5' : ''}>
            <CardContent className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${alert.severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-500' : 'bg-amber-500/10 text-amber-500'}`}>
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono font-bold text-slate-900 dark:text-slate-100 text-sm">
                      {alert.id} • {alert.machineId}
                    </span>
                    <StatusBadge status={alert.severity} size="sm" />
                    <span className="text-[11px] text-slate-400 font-mono">{alert.detectedAt}</span>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1">{alert.title}</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{alert.description}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 self-end md:self-center">
                {alert.status === 'ACTIVE' ? (
                  <Button size="sm" variant="secondary" onClick={() => handleAcknowledge(alert.id)}>
                    Acknowledge
                  </Button>
                ) : (
                  <span className="text-xs font-semibold text-emerald-500 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Acknowledged
                  </span>
                )}
                <Link to={`/machines/${alert.machineId}`}>
                  <Button size="sm" variant="ai" leftIcon={<Bot className="w-3.5 h-3.5" />}>
                    AI Investigate
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
