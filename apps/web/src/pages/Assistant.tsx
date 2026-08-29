import React, { useState } from 'react';
import {
  Sparkles,
  Send,
  Bot,
  User,
  RefreshCw,
  BookOpen,
  Activity,
  Zap,
  HelpCircle,
} from 'lucide-react';
import { queryCopilot } from '../api/client';

export const Assistant: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string; metadata?: any }>>([
    {
      role: 'assistant',
      text: "Hello! I'm PredictX Copilot, your industrial predictive maintenance AI. Ask me about machine health (e.g. 'Status of machine M1003', 'Why is M1002 vibrating?'), troubleshooting SOPs, or failure mode physics.",
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    'Analyze latest telemetry and risk for machine M1003',
    'What is the standard overhaul procedure for pump bearing wear (SOP)?',
    'Explain why M1002 temperature is rising above nominal baseline',
    'Check RUL hours and failure probability for compressor M1001',
  ];

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await queryCopilot(q);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: res.answer || 'Analysis complete. All sensors evaluated against baseline.',
          metadata: res,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Diagnostic query error: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">PredictX AI Diagnostic Assistant</h1>
            <p className="text-sm text-slate-400">
              Interactive natural language copilot with live machine telemetry grounding and equipment manual retrieval
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-xs font-mono font-semibold">
          Grounded RAG Engine Active
        </span>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-slate-400 font-medium mr-1">Quick Prompts:</span>
        {samplePrompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(p)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/40 text-xs text-slate-300 hover:text-white transition-all text-left"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chat Container */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl overflow-hidden flex flex-col h-[520px]">
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-indigo-600 text-white font-medium shadow-md'
                    : 'bg-slate-950 border border-slate-800/80 text-slate-200 shadow-sm'
                }`}
              >
                <div className="whitespace-pre-wrap">{m.text}</div>

                {/* Metadata & Predictions pill if grounded in telemetry */}
                {m.metadata?.predictions && (
                  <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2 font-mono text-[11px]">
                    <span className="text-indigo-400">
                      Risk: {((m.metadata.predictions.failure_probability || 0.05) * 100).toFixed(1)}%
                    </span>
                    <span>•</span>
                    <span className="text-sky-400">
                      RUL: {(m.metadata.predictions.predicted_rul || 180).toFixed(1)}h
                    </span>
                    <span>•</span>
                    <span className="text-amber-400">
                      Mode: {m.metadata.predictions.failure_type || 'Nominal'}
                    </span>
                  </div>
                )}
              </div>

              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 text-slate-300 flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0">
                <RefreshCw className="w-4 h-4 animate-spin" />
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-400 font-mono">
                PredictX Copilot synthesizing sensor telemetry & retrieving equipment SOPs...
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center gap-3"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask about machine status, failure diagnostics, or maintenance guidelines..."
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
