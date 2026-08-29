const API_BASE = "http://127.0.0.1:8000/api/v1";

export type UserRole = "VIEWER" | "OPERATOR" | "ENGINEER" | "ADMIN";

export interface UserProfile {
  username: string;
  role: UserRole;
  name?: string;
  title?: string;
  issued_at?: number;
  expires_at?: number;
  access_token: string;
}

export interface TelemetryPayload {
  machine_code?: string;
  temperature: number;
  vibration: number;
  pressure: number;
  rpm: number;
  voltage: number;
  current: number;
  power?: number;
  humidity?: number;
  load?: number;
  operating_hours?: number;
  maintenance_count?: number;
}

export interface PredictionResult {
  status: string;
  machine_code: string;
  health_status: "HEALTHY" | "WARNING" | "HIGH_RISK" | "CRITICAL";
  health_badge: string;
  threat_color: string;
  failure_probability: number;
  estimated_rul_hours: number;
  rul_confidence_interval: [number, number];
  anomaly_severity: string;
  predicted_failure_mode: string;
  root_cause_explanation: string;
  explainability: Array<{
    feature: string;
    value: string;
    baseline: string;
    delta: string;
    weight: number;
    severity: string;
  }>;
  timestamp: string;
}

function getAuthHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = localStorage.getItem("predictx_jwt_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ---------------- AUTHENTICATION & RBAC ----------------

export async function loginUser(username: string, password: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Authentication failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`Failed to fetch user profile: ${res.statusText}`);
  return res.json();
}

export async function fetchRolesList() {
  const res = await fetch(`${API_BASE}/auth/roles`);
  if (!res.ok) throw new Error(`Failed to fetch roles: ${res.statusText}`);
  return res.json();
}

// ---------------- TELEMETRY & PREDICTIONS ----------------

export async function fetchMachines() {
  const res = await fetch(`${API_BASE}/machines`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load machines: ${res.statusText}`);
  return res.json();
}

export async function fetchMachinePredictions(machineCode: string) {
  const res = await fetch(`${API_BASE}/predictions/${machineCode}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load predictions: ${res.statusText}`);
  return res.json();
}

export async function predictDirect(telemetry: TelemetryPayload): Promise<PredictionResult> {
  const res = await fetch(`${API_BASE}/predict/direct`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(telemetry),
  });
  if (!res.ok) throw new Error(`Inference request failed: ${res.statusText}`);
  return res.json();
}

export async function fetchFleetPredictions() {
  const res = await fetch(`${API_BASE}/fleet/predictions`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load fleet predictions: ${res.statusText}`);
  return res.json();
}

// ---------------- MODEL REGISTRY & DRIFT ----------------

export async function fetchRegisteredModels() {
  const res = await fetch(`${API_BASE}/models`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load models: ${res.statusText}`);
  return res.json();
}

export async function fetchDriftStatus() {
  const res = await fetch(`${API_BASE}/monitoring/drift`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load drift metrics: ${res.statusText}`);
  return res.json();
}

export async function triggerRetraining(task: string, force = false) {
  const res = await fetch(`${API_BASE}/retrain`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ task, force }),
  });
  if (!res.ok) throw new Error(`Retraining trigger failed: ${res.statusText}`);
  return res.json();
}

// ---------------- RAG KNOWLEDGE BASE & COPILOT ----------------

export async function fetchKnowledgeDocuments() {
  const res = await fetch(`${API_BASE}/rag/documents`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load manuals: ${res.statusText}`);
  return res.json();
}

export async function searchRAG(query: string, top_k = 5) {
  const res = await fetch(`${API_BASE}/rag/search`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ query, top_k }),
  });
  if (!res.ok) throw new Error(`RAG search failed: ${res.statusText}`);
  return res.json();
}

export async function queryCopilot(query: string) {
  const res = await fetch(`${API_BASE}/copilot/query`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`Copilot query failed: ${res.statusText}`);
  return res.json();
}

// ---------------- AGENT FLEET & MCP ----------------

export async function fetchAgentFleet() {
  const res = await fetch(`${API_BASE}/agents/fleet`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load agent fleet: ${res.statusText}`);
  return res.json();
}

export async function runAgentInvestigation(machine_code: string, telemetry?: any) {
  const res = await fetch(`${API_BASE}/agents/investigate`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ machine_code, telemetry }),
  });
  if (!res.ok) throw new Error(`Agent investigation failed: ${res.statusText}`);
  return res.json();
}

export async function fetchMCPServers() {
  const res = await fetch(`${API_BASE}/mcp/servers`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load MCP servers: ${res.statusText}`);
  return res.json();
}

export async function executeMCPTool(tool_name: string, args: Record<string, any> = {}) {
  const res = await fetch(`${API_BASE}/mcp/execute`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ tool_name, arguments: args }),
  });
  if (!res.ok) throw new Error(`MCP tool execution failed: ${res.statusText}`);
  return res.json();
}

// ---------------- HITL APPROVAL & AUDIT ----------------

export async function fetchHITLPendingRequests() {
  const res = await fetch(`${API_BASE}/hitl/requests`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load HITL requests: ${res.statusText}`);
  return res.json();
}

export async function approveHITLRequest(request_id: string, approver_id: string, notes?: string) {
  const res = await fetch(`${API_BASE}/hitl/approve`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ request_id, approver_id, notes }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Approval failed: ${res.statusText}`);
  }
  return res.json();
}

export async function rejectHITLRequest(request_id: string, rejecter_id: string, reason: string) {
  const res = await fetch(`${API_BASE}/hitl/reject`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ request_id, rejecter_id, reason }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Rejection failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchAuditTrail(machine_id?: string) {
  const url = machine_id ? `${API_BASE}/hitl/audit?machine_id=${machine_id}` : `${API_BASE}/hitl/audit`;
  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load audit trail: ${res.statusText}`);
  return res.json();
}

// ---------------- INCIDENTS & WORK ORDERS ----------------

export async function fetchIncidents() {
  const res = await fetch(`${API_BASE}/incidents`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load incidents: ${res.statusText}`);
  return res.json();
}

export async function fetchWorkOrders() {
  const res = await fetch(`${API_BASE}/work-orders`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load work orders: ${res.statusText}`);
  return res.json();
}

export async function fetchObservabilityStats() {
  const res = await fetch(`${API_BASE}/observability/stats`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to load observability stats: ${res.statusText}`);
  return res.json();
}
