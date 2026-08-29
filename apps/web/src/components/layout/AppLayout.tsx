import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { CommandPalette } from './CommandPalette';
import { LoginModal } from '../auth/LoginModal';
import { Drawer } from '../ui/Drawer';
import { Sparkles, Send, Bot, AlertTriangle, CheckCircle2, BookOpen, ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';

export const AppLayout: React.FC = () => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [assistantQuery, setAssistantQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string; structured?: any; sources?: string[] }>>([
    {
      role: 'assistant',
      text: 'PredictX AI Copilot active. Continuous ingestion connected to 1,248 machines. Machine M1047 exhibits critical vibration harmonic degradation (87% failure probability). How can I assist you?',
      structured: {
        severity: 'CRITICAL',
        target: 'Machine M1047 (CNC #4)',
        risk: '87% Failure Probability',
        rul: '143 Operating Hours Remaining',
        diagnosis: 'Bearing Wear / Radial Vibration Harmonic Breach (4.25 mm/s > 3.5 mm/s limit)',
        recommendation: 'Replace 2x SKF-6205 drive bearings under LOTO safety protocol.',
      },
      sources: ['SKF Bearing Reliability Guide v3.1', 'Telemetry Stream Partition #0'],
    },
  ]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSendMessage = (e?: React.FormEvent, customPrompt?: string) => {
    if (e) e.preventDefault();
    const query = customPrompt || assistantQuery;
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', text: query }]);
    setAssistantQuery('');

    // Simulate Agent diagnostic response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Analysis complete for: "${query}". Root cause correlation and RAG engineering manuals confirm equipment degradation profile.`,
          structured: {
            severity: 'CRITICAL',
            target: 'M1047 - Plant A',
            risk: '87% Probability',
            rul: '143 Hours',
            diagnosis: 'High harmonic vibration spike (4.25 mm/s) + 78.4°C drive temperature rise.',
            recommendation: 'Pre-staged Work Order WO-M1047-01 with parts SKF-6205-2RSH and grease.',
          },
          sources: ['Standard Operating Procedure SOP-704', 'Historical Work Orders DB'],
        },
      ]);
    }, 500);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 antialiased overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#090d16]">
        <TopNav
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
          onOpenAssistant={() => setIsAssistantOpen(true)}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
          <Outlet />
        </main>
      </div>

      {/* Login / RBAC Switcher Modal & Command Palette */}
      <LoginModal />
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />

      {/* AI Assistant Right Drawer */}
      <Drawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        title="PredictX Reliability Copilot"
        subtitle="Hybrid RAG + Multi-Agent Industrial Intelligence"
        width="lg"
      >
        <div className="flex flex-col h-full space-y-4">
          {/* Quick Prompt Chips */}
          <div className="flex flex-wrap gap-1.5 pb-2 border-b border-slate-800">
            <button
              onClick={() => handleSendMessage(undefined, 'Analyze health of machine M1047')}
              className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
            >
              ⚡ Analyze M1047
            </button>
            <button
              onClick={() => handleSendMessage(undefined, 'Why is vibration high on M1047?')}
              className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
            >
              🔍 Root Cause Vibration
            </button>
            <button
              onClick={() => handleSendMessage(undefined, 'Show bearing repair SOP')}
              className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
            >
              📖 Bearing SOP Manual
            </button>
          </div>

          {/* Messages Feed with Ultra-Legible Contrast */}
          <div className="flex-1 overflow-y-auto space-y-4 pr-1">
            {messages.map((m, idx) => (
              <div key={idx} className="space-y-2">
                {m.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className="bg-brand-600 text-white font-medium text-xs px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-[85%] shadow-md">
                      {m.text}
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-850 bg-[#111827] border border-slate-800 p-4 rounded-2xl rounded-tl-sm text-xs text-slate-100 shadow-xl space-y-3">
                    {/* Header */}
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-slate-300">
                      <div className="flex items-center gap-2 font-bold text-white">
                        <div className="w-5 h-5 rounded bg-violet-600 flex items-center justify-center text-white">
                          <Sparkles className="w-3 h-3" />
                        </div>
                        <span>PredictX Intelligence</span>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-semibold">
                        Grounded RAG
                      </span>
                    </div>

                    <p className="text-slate-200 text-xs leading-relaxed">{m.text}</p>

                    {/* Structured Assessment Box */}
                    {m.structured && (
                      <div className="p-3.5 rounded-xl bg-[#090d16] border border-slate-800 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-slate-400 uppercase">Operational Diagnostic</span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            {m.structured.severity}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300 pt-1">
                          <div>
                            <span className="text-slate-500 block">Target:</span>
                            <span className="font-semibold text-white">{m.structured.target}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Estimated RUL:</span>
                            <span className="font-semibold text-rose-400">{m.structured.rul}</span>
                          </div>
                        </div>

                        <div className="text-[11px] pt-1 text-slate-300">
                          <span className="text-slate-500 block">Diagnosis:</span>
                          <span className="text-slate-200 font-medium">{m.structured.diagnosis}</span>
                        </div>

                        <div className="text-[11px] p-2 rounded bg-slate-800/80 text-slate-200 border border-slate-700">
                          <strong className="text-emerald-400">Action Plan: </strong>
                          {m.structured.recommendation}
                        </div>
                      </div>
                    )}

                    {/* Citations */}
                    {m.sources && (
                      <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex items-center gap-1.5">
                        <BookOpen className="w-3 h-3 text-slate-400" />
                        <span className="font-semibold text-slate-400">Indexed Sources:</span>
                        <span className="text-slate-300">{m.sources.join(' • ')}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Prompt Input Form */}
          <form onSubmit={handleSendMessage} className="flex gap-2 pt-2 border-t border-slate-800">
            <input
              type="text"
              placeholder="Ask Copilot about machine faults or manuals..."
              value={assistantQuery}
              onChange={(e) => setAssistantQuery(e.target.value)}
              className="flex-1 px-4 py-2.5 text-xs rounded-xl border border-slate-700 bg-slate-800 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <Button size="sm" variant="ai" type="submit">
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Drawer>
    </div>
  );
};
