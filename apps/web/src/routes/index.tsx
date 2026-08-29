import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { Dashboard } from '../pages/Dashboard';
import { Machines } from '../pages/Machines';
import { MachineDetails } from '../pages/MachineDetails';
import { LiveTelemetry } from '../pages/LiveTelemetry';
import { Alerts } from '../pages/Alerts';
import { Investigations } from '../pages/Investigations';
import { Predictions } from '../pages/Predictions';
import { Models } from '../pages/Models';
import { DriftDetection } from '../pages/DriftDetection';
import { KnowledgeBase } from '../pages/KnowledgeBase';
import { AgentFleet } from '../pages/AgentFleet';
import { MCPTools } from '../pages/MCPTools';
import { WorkOrders } from '../pages/WorkOrders';
import { AuditLogs } from '../pages/AuditLogs';
import { Observability } from '../pages/Observability';
import { Assistant } from '../pages/Assistant';
import { Incidents } from '../pages/Incidents';
import { RolesAndPermissions } from '../pages/RolesAndPermissions';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import {
  Wrench,
  History,
  FlaskConical,
  LineChart,
  ShieldCheck,
  UserCheck,
  ShieldAlert,
  Settings,
} from 'lucide-react';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* Default redirect to Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* OVERVIEW */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* MONITORING */}
        <Route path="/machines" element={<Machines />} />
        <Route path="/machines/:id" element={<MachineDetails />} />
        <Route path="/live-telemetry" element={<LiveTelemetry />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/incidents" element={<Incidents />} />

        {/* MAINTENANCE */}
        <Route
          path="/maintenance"
          element={
            <PlaceholderPage
              title="Preventive Maintenance"
              subtitle="Scheduled maintenance interventions and automated work order queue."
              section="MAINTENANCE"
              icon={Wrench}
            />
          }
        />
        <Route path="/work-orders" element={<WorkOrders />} />
        <Route
          path="/maintenance-history"
          element={
            <PlaceholderPage
              title="Maintenance History & Verification"
              subtitle="Historical maintenance records with post-repair telemetry verification comparisons."
              section="MAINTENANCE"
              icon={History}
            />
          }
        />

        {/* AI & INTELLIGENCE */}
        <Route path="/investigations" element={<Investigations />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/rag-search" element={<KnowledgeBase />} />
        <Route path="/assistant" element={<Assistant />} />

        {/* ML PLATFORM */}
        <Route path="/models" element={<Models />} />
        <Route
          path="/experiments"
          element={
            <PlaceholderPage
              title="ML Experiments"
              subtitle="Hyperparameter tuning, cross-validation metrics, and training run tracking."
              section="ML PLATFORM"
              icon={FlaskConical}
            />
          }
        />
        <Route
          path="/model-monitoring"
          element={
            <PlaceholderPage
              title="Model Monitoring & Performance"
              subtitle="Inference latency, accuracy distributions, and prediction reliability scores."
              section="ML PLATFORM"
              icon={LineChart}
            />
          }
        />
        <Route path="/drift-detection" element={<DriftDetection />} />
        <Route path="/retraining" element={<DriftDetection />} />

        {/* OPERATIONS */}
        <Route path="/agents" element={<AgentFleet />} />
        <Route path="/mcp" element={<MCPTools />} />
        <Route
          path="/evaluations"
          element={
            <PlaceholderPage
              title="Evaluation & Benchmarks"
              subtitle="RAG Triad metrics (Context Relevance, Faithfulness, Answer Relevance) and HitRate@K."
              section="OPERATIONS"
              icon={ShieldCheck}
            />
          }
        />
        <Route path="/observability" element={<Observability />} />

        {/* ADMINISTRATION */}
        <Route
          path="/users"
          element={
            <PlaceholderPage
              title="User Management"
              subtitle="Platform user directory and authentication profiles."
              section="ADMINISTRATION"
              icon={UserCheck}
            />
          }
        />
        <Route path="/roles" element={<RolesAndPermissions />} />
        <Route path="/audit-logs" element={<AuditLogs />} />
        <Route
          path="/settings"
          element={
            <PlaceholderPage
              title="System Settings"
              subtitle="Environment configuration, Kafka broker endpoints, and API security keys."
              section="ADMINISTRATION"
              icon={Settings}
            />
          }
        />

        {/* 404 Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
};
