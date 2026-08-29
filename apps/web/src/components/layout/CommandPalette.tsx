import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Cpu,
  AlertTriangle,
  BookOpen,
  Layers,
  Bot,
  ArrowRight,
  X,
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface SearchItem {
  id: string;
  title: string;
  category: 'MACHINES' | 'ALERTS' | 'DOCUMENTS' | 'MODELS' | 'AGENTS';
  subtitle: string;
  href: string;
  status?: string;
}

const SEARCH_DATABASE: SearchItem[] = [
  { id: '1', title: 'M1047', category: 'MACHINES', subtitle: 'CNC Milling Machine • Plant A', href: '/machines/M1047', status: 'CRITICAL' },
  { id: '2', title: 'M2083', category: 'MACHINES', subtitle: 'Centrifugal Slurry Pump • Plant B', href: '/machines/M2083', status: 'WARNING' },
  { id: '3', title: 'M3012', category: 'MACHINES', subtitle: 'High-Pressure Compressor • Plant A', href: '/machines/M3012', status: 'HEALTHY' },
  { id: '4', title: 'Critical Vibration Harmonic Anomaly', category: 'ALERTS', subtitle: 'Vibration 4.2 mm/s exceeds 3.5 mm/s limit on M1047', href: '/alerts', status: 'CRITICAL' },
  { id: '5', title: 'Hydraulic Pressure Loss Alarm', category: 'ALERTS', subtitle: 'Chamber pressure dropped to 72 PSI on M2083', href: '/alerts', status: 'HIGH' },
  { id: '6', title: 'Bearing Wear SOP & Maintenance Guide', category: 'DOCUMENTS', subtitle: 'Standard manual for SKF deep groove ball bearings (v3.1)', href: '/knowledge' },
  { id: '7', title: 'Cooling Line Descaling Procedure', category: 'DOCUMENTS', subtitle: 'Weekly radiator maintenance & glycol fluid flush', href: '/knowledge' },
  { id: '8', title: 'Failure Threat Classifier (XGBoost)', category: 'MODELS', subtitle: 'v3.2.0 • Accuracy 94.2% • Production', href: '/models' },
  { id: '9', title: 'RUL Degradation Estimator (Random Forest)', category: 'MODELS', subtitle: 'v2.1.0 • RMSE 4.8h • Production', href: '/models' },
  { id: '10', title: 'Root Cause Analysis (RCA) Agent', category: 'AGENTS', subtitle: 'Correlates sensor anomalies with physics failure trees', href: '/agents' },
];

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        isOpen ? onClose() : undefined;
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = query.trim()
    ? SEARCH_DATABASE.filter(
        (item) =>
          item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.subtitle.toLowerCase().includes(query.toLowerCase()) ||
          item.category.toLowerCase().includes(query.toLowerCase())
      )
    : SEARCH_DATABASE.slice(0, 6);

  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case 'MACHINES':
        return <Cpu className="w-4 h-4 text-brand-500" />;
      case 'ALERTS':
        return <AlertTriangle className="w-4 h-4 text-rose-500" />;
      case 'DOCUMENTS':
        return <BookOpen className="w-4 h-4 text-emerald-500" />;
      case 'MODELS':
        return <Layers className="w-4 h-4 text-indigo-500" />;
      case 'AGENTS':
        return <Bot className="w-4 h-4 text-violet-500" />;
      default:
        return <Search className="w-4 h-4 text-slate-400" />;
    }
  };

  const handleSelect = (href: string) => {
    navigate(href);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto p-4 sm:p-6 md:p-20">
      <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity" onClick={onClose} />

      <div className="relative mx-auto max-w-2xl transform overflow-hidden rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-2xl transition-all">
        {/* Search Input */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-100 dark:border-slate-800">
          <Search className="w-5 h-5 text-slate-400 mr-3" />
          <input
            type="text"
            className="w-full bg-transparent border-0 text-sm font-medium text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none"
            placeholder="Search machines, alerts, SOPs, models, agents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-slate-100 dark:divide-slate-800/40">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No results found for "{query}"
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                onClick={() => handleSelect(item.href)}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/60 cursor-pointer transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {getCategoryIcon(item.category)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">{item.title}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-medium">
                        {item.category}
                      </span>
                      {item.status && (
                        <span
                          className={cn(
                            'text-[10px] px-1.5 py-0.2 rounded font-semibold',
                            item.status === 'CRITICAL'
                              ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                              : 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                          )}
                        >
                          {item.status}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400">{item.subtitle}</p>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-brand-500 group-hover:translate-x-0.5 transition-all" />
              </div>
            ))
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2 bg-slate-50 dark:bg-navy-950/60 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>Navigation:</span>
            <kbd className="font-mono text-[10px] px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-800">↑↓</kbd>
            <span>Select:</span>
            <kbd className="font-mono text-[10px] px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-800">Enter</kbd>
          </div>
          <div>
            <kbd className="font-mono text-[10px] px-1 py-0.5 rounded bg-slate-200 dark:bg-slate-800">ESC</kbd> to close
          </div>
        </div>
      </div>
    </div>
  );
};
