import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Cpu,
  Radio,
  RefreshCw,
  Zap,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Button } from '../components/ui/Button';

interface SensorStreamItem {
  id: string;
  name: string;
  value: number;
  unit: string;
  nominalRange: string;
  delta: number;
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
}

const INITIAL_SENSORS: SensorStreamItem[] = [
  { id: 'vib', name: 'Radial Vibration (RMS)', value: 4.25, unit: 'mm/s', nominalRange: '0.5 – 2.5 mm/s', delta: +14.2, status: 'CRITICAL' },
  { id: 'temp', name: 'Drive Temperature', value: 78.4, unit: '°C', nominalRange: '50.0 – 65.0 °C', delta: +8.3, status: 'WARNING' },
  { id: 'press', name: 'Hydraulic Pressure', value: 98.2, unit: 'PSI', nominalRange: '90.0 – 110.0 PSI', delta: -1.2, status: 'HEALTHY' },
  { id: 'rpm', name: 'Motor Spindle RPM', value: 1850, unit: 'RPM', nominalRange: '1750 – 1850 RPM', delta: +0.4, status: 'HEALTHY' },
  { id: 'current', name: 'Phase Current (RMS)', value: 14.8, unit: 'A', nominalRange: '8.0 – 12.0 A', delta: +6.5, status: 'WARNING' },
  { id: 'power', name: '3-Phase Active Power', value: 6.2, unit: 'kW', nominalRange: '3.0 – 5.5 kW', delta: +5.1, status: 'WARNING' },
  { id: 'voltage', name: 'Bus Line Voltage', value: 415.2, unit: 'V', nominalRange: '400.0 – 430.0 V', delta: -0.1, status: 'HEALTHY' },
  { id: 'load', name: 'Motor Load Ratio', value: 84.5, unit: '%', nominalRange: '40.0 – 80.0 %', delta: +4.2, status: 'WARNING' },
  { id: 'humidity', name: 'Chamber Humidity', value: 42.0, unit: '%', nominalRange: '30.0 – 55.0 %', delta: +0.0, status: 'HEALTHY' },
];

export const LiveTelemetry: React.FC = () => {
  const [sensors, setSensors] = useState<SensorStreamItem[]>(INITIAL_SENSORS);
  const [isStreaming, setIsStreaming] = useState(true);
  const [updateCount, setUpdateCount] = useState(1);

  // Simulate real-time streaming sensor jitter
  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(() => {
      setSensors((prev) =>
        prev.map((s) => {
          const jitter = (Math.random() - 0.48) * (s.value * 0.02);
          const newVal = Number((s.value + jitter).toFixed(s.unit === 'RPM' ? 0 : 2));
          return {
            ...s,
            value: newVal,
          };
        })
      );
      setUpdateCount((c) => c + 1);
    }, 2000);

    return () => clearInterval(interval);
  }, [isStreaming]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Live Sensor Telemetry Stream
            </h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Kafka Stream • Partition 0 • 100 Hz
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time multi-channel sensor ingestion for active machine <strong className="text-slate-800 dark:text-slate-200">M1047 (CNC #4)</strong>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={isStreaming ? 'outline' : 'primary'}
            onClick={() => setIsStreaming(!isStreaming)}
          >
            {isStreaming ? 'Pause Stream' : 'Resume Live Stream'}
          </Button>
        </div>
      </div>

      {/* Sensor Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors.map((s) => (
          <Card key={s.id} hoverable className={s.status === 'CRITICAL' ? 'border-rose-500/40 bg-rose-500/5' : ''}>
            <CardContent className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate">{s.name}</span>
                <StatusBadge status={s.status} size="sm" />
              </div>

              <div className="flex items-baseline justify-between">
                <div className="text-3xl font-bold font-mono text-slate-900 dark:text-slate-100">
                  {s.value}
                  <span className="text-xs font-normal text-slate-400 ml-1.5">{s.unit}</span>
                </div>

                <div className={`flex items-center text-xs font-semibold ${s.delta > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                  {s.delta > 0 ? <ArrowUp className="w-3.5 h-3.5 mr-0.5" /> : <ArrowDown className="w-3.5 h-3.5 mr-0.5" />}
                  {Math.abs(s.delta)}%
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <span>Normal: <strong className="text-slate-600 dark:text-slate-300 font-mono">{s.nominalRange}</strong></span>
                <span className="font-mono text-[10px] text-slate-400">Pkt #{updateCount}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
