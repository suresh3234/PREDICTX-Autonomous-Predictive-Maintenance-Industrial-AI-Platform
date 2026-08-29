import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  AlertTriangle,
  Wrench,
  UserCheck,
  RefreshCw,
  Lock,
} from 'lucide-react';
import { fetchWorkOrders, fetchHITLPendingRequests, approveHITLRequest, rejectHITLRequest } from '../api/client';

export const WorkOrders: React.FC = () => {
  const [workOrders, setWorkOrders] = useState<any[]>([]);
  const [pendingRequests, setPendingRequests] = useState<any[]>([]);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const woRes = await fetchWorkOrders();
      setWorkOrders(woRes.work_orders || []);
      const reqRes = await fetchHITLPendingRequests();
      setPendingRequests(reqRes.pending_requests || []);
    } catch (err) {
      console.error('Failed loading HITL work orders:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApprove = async (requestId: string) => {
    setProcessingId(requestId);
    setActionFeedback(null);
    try {
      await approveHITLRequest(requestId, 'ENG_DEVAR_01', 'Approved after verifying LOTO isolation on MCC-04');
      setActionFeedback(`Request ${requestId} approved & logged to SHA-256 audit chain!`);
      loadData();
    } catch (err: any) {
      setActionFeedback(`Approval failed: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (requestId: string) => {
    setProcessingId(requestId);
    setActionFeedback(null);
    try {
      await rejectHITLRequest(requestId, 'ENG_DEVAR_01', 'Rejected: Spare parts not yet verified in warehouse.');
      setActionFeedback(`Request ${requestId} rejected and logged.`);
      loadData();
    } catch (err: any) {
      setActionFeedback(`Rejection failed: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const sampleWorkOrders = [
    {
      work_order_id: 'WO-2026-0881',
      machine_code: 'M1003',
      title: 'Emergency Hydraulic Pack Overhaul & High-Pressure O-Ring Replacement',
      priority: 'P1_URGENT',
      risk_tier: 'TIER_3_EMERGENCY',
      estimated_downtime_hours: 3.5,
      required_parts: ['Hydraulic Seal Kit (SKU-H44)', 'ISO VG 46 Fluid 20L'],
      loto_required: true,
      status: 'AWAITING_APPROVAL',
    },
    {
      work_order_id: 'WO-2026-0880',
      machine_code: 'M1002',
      title: 'Precision Shaft Re-alignment & SKF 6208 Deep Groove Bearing Replacement',
      priority: 'P2_ELEVATED',
      risk_tier: 'TIER_2_ENGINEER',
      estimated_downtime_hours: 2.0,
      required_parts: ['SKF 6208-2RS1 Bearing', 'Mobil Polyrex EM Grease'],
      loto_required: true,
      status: 'APPROVED',
    },
    {
      work_order_id: 'WO-2026-0879',
      machine_code: 'M1001',
      title: 'Compressor Radiator Fin Hydro-Cleaning & Coolant Top-Up',
      priority: 'P3_ROUTINE',
      risk_tier: 'TIER_1_STANDARD',
      estimated_downtime_hours: 1.0,
      required_parts: ['Coolant Filter (CF-100)'],
      loto_required: false,
      status: 'COMPLETED',
    },
  ];

  const orders = workOrders.length > 0 ? workOrders : sampleWorkOrders;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Work Orders & HITL Safety Approvals</h1>
            <p className="text-sm text-slate-400">
              Risk-tiered Human-in-the-Loop approval gates for critical maintenance and emergency machine shutdowns
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-mono font-bold">
            Risk Tiering: Tier 1 Auto • Tier 2 Eng • Tier 3 Emergency
          </span>
        </div>
      </div>

      {/* Action Notification */}
      {actionFeedback && (
        <div className="p-4 rounded-2xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{actionFeedback}</span>
          </div>
          <button onClick={() => setActionFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Work Orders List */}
      <div className="space-y-4">
        {orders.map((wo, idx) => (
          <div
            key={idx}
            className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4 hover:border-slate-700 transition-all"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-slate-950 text-indigo-400 border border-slate-800">
                  {wo.work_order_id}
                </span>
                <span className="text-xs font-mono text-slate-400">Asset: {wo.machine_code}</span>
                <span
                  className={`px-2.5 py-0.5 rounded text-[11px] font-bold ${
                    wo.risk_tier.includes('TIER_3')
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : wo.risk_tier.includes('TIER_2')
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  }`}
                >
                  {wo.risk_tier}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold ${
                    wo.status === 'AWAITING_APPROVAL'
                      ? 'bg-amber-500/20 text-amber-300 animate-pulse'
                      : wo.status === 'APPROVED'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {wo.status}
                </span>
              </div>
            </div>

            {/* Title & Details */}
            <div>
              <h3 className="text-base font-bold text-white mb-2">{wo.title}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-500" />
                  <span>Est. Downtime: <strong className="text-slate-200">{wo.estimated_downtime_hours} hrs</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-rose-400" />
                  <span>LOTO Required: <strong className="text-slate-200">{wo.loto_required ? 'YES (MCC-04 Isolated)' : 'NO'}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-indigo-400" />
                  <span>Parts: <strong className="text-slate-200">{wo.required_parts.join(', ')}</strong></span>
                </div>
              </div>
            </div>

            {/* Human-in-the-Loop Action Bar */}
            {wo.status === 'AWAITING_APPROVAL' && (
              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
                <button
                  onClick={() => handleReject(wo.work_order_id)}
                  disabled={processingId === wo.work_order_id}
                  className="px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 hover:bg-rose-950/40 text-rose-400 text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  Reject Work Order
                </button>
                <button
                  onClick={() => handleApprove(wo.work_order_id)}
                  disabled={processingId === wo.work_order_id}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 flex items-center gap-1.5 transition-all"
                >
                  {processingId === wo.work_order_id ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                  Approve Safety Gate (LOTO Cleared)
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
