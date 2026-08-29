export interface Machine {
  id: string;
  code: string;
  name: string;
  type: string;
  plant: string;
  healthScore: number;
  riskScore: number;
  failureProbability: number;
  rulHours: number;
  predictedFailureType: string;
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'OFFLINE';
  anomalyScore: number;
  lastMaintenance: string;
  operatingHours: number;
  sensors: {
    temperature: number;
    vibration: number;
    pressure: number;
    rpm: number;
    current: number;
    power: number;
    voltage: number;
  };
}

export const MOCK_MACHINES: Machine[] = [
  {
    id: 'M1047',
    code: 'M1047',
    name: 'CNC 5-Axis Milling Center #4',
    type: 'CNC Milling',
    plant: 'Plant A - Ohio',
    healthScore: 34,
    riskScore: 87,
    failureProbability: 0.87,
    rulHours: 143,
    predictedFailureType: 'Bearing Wear / Shaft Misalignment',
    status: 'CRITICAL',
    anomalyScore: 0.91,
    lastMaintenance: '12 days ago',
    operatingHours: 4120,
    sensors: {
      temperature: 78.4,
      vibration: 4.25,
      pressure: 98.2,
      rpm: 1850,
      current: 14.8,
      power: 6.2,
      voltage: 415.0,
    },
  },
  {
    id: 'M2083',
    code: 'M2083',
    name: 'High-Volume Centrifugal Slurry Pump',
    type: 'Industrial Pump',
    plant: 'Plant B - Texas',
    healthScore: 68,
    riskScore: 42,
    failureProbability: 0.42,
    rulHours: 380,
    predictedFailureType: 'Hydraulic Seal Rupture',
    status: 'WARNING',
    anomalyScore: 0.54,
    lastMaintenance: '5 days ago',
    operatingHours: 2950,
    sensors: {
      temperature: 64.2,
      vibration: 2.15,
      pressure: 74.0,
      rpm: 1480,
      current: 11.2,
      power: 4.1,
      voltage: 400.0,
    },
  },
  {
    id: 'M3012',
    code: 'M3012',
    name: 'High-Pressure Screw Compressor A',
    type: 'Compressor',
    plant: 'Plant A - Ohio',
    healthScore: 92,
    riskScore: 8,
    failureProbability: 0.08,
    rulHours: 920,
    predictedFailureType: 'None (Nominal)',
    status: 'HEALTHY',
    anomalyScore: 0.12,
    lastMaintenance: '2 days ago',
    operatingHours: 1240,
    sensors: {
      temperature: 52.8,
      vibration: 1.20,
      pressure: 104.5,
      rpm: 1520,
      current: 9.8,
      power: 3.6,
      voltage: 400.0,
    },
  },
  {
    id: 'M4120',
    code: 'M4120',
    name: 'Gas Turbine Generator #2',
    type: 'Turbine',
    plant: 'Plant C - Nevada',
    healthScore: 48,
    riskScore: 74,
    failureProbability: 0.74,
    rulHours: 210,
    predictedFailureType: 'Thermal Dissipation Failure',
    status: 'WARNING',
    anomalyScore: 0.78,
    lastMaintenance: '18 days ago',
    operatingHours: 6840,
    sensors: {
      temperature: 88.6,
      vibration: 2.80,
      pressure: 91.0,
      rpm: 3600,
      current: 13.5,
      power: 8.4,
      voltage: 420.0,
    },
  },
  {
    id: 'M5091',
    code: 'M5091',
    name: 'Heavy Hydraulic Stamping Press 500T',
    type: 'Hydraulic Press',
    plant: 'Plant A - Ohio',
    healthScore: 88,
    riskScore: 12,
    failureProbability: 0.12,
    rulHours: 780,
    predictedFailureType: 'None (Nominal)',
    status: 'HEALTHY',
    anomalyScore: 0.18,
    lastMaintenance: '4 days ago',
    operatingHours: 3100,
    sensors: {
      temperature: 58.0,
      vibration: 1.45,
      pressure: 102.0,
      rpm: 1200,
      current: 10.4,
      power: 4.8,
      voltage: 405.0,
    },
  },
];

export const MOCK_ALERTS = [
  {
    id: 'ALT-101',
    machineId: 'M1047',
    severity: 'CRITICAL',
    title: 'Severe Vibration Harmonic Anomaly',
    description: 'Radial vibration of 4.25 mm/s exceeds 3.5 mm/s ISO limit. High probability of bearing race spalling.',
    detectedAt: '2 minutes ago',
    failureProbability: 87,
    rulHours: 143,
    status: 'ACTIVE',
  },
  {
    id: 'ALT-102',
    machineId: 'M4120',
    severity: 'HIGH',
    title: 'Thermal Dissipation Degradation',
    description: 'Cooling line delta temp exceeds 88.6°C. Clogged radiator mesh detected.',
    detectedAt: '14 minutes ago',
    failureProbability: 74,
    rulHours: 210,
    status: 'ACTIVE',
  },
  {
    id: 'ALT-103',
    machineId: 'M2083',
    severity: 'MEDIUM',
    title: 'Hydraulic Pressure Drop',
    description: 'Chamber pressure 74 PSI below nominal 90 PSI baseline. Potential O-ring gasket tear.',
    detectedAt: '38 minutes ago',
    failureProbability: 42,
    rulHours: 380,
    status: 'ACKNOWLEDGED',
  },
];

export const MOCK_WORK_ORDERS = [
  {
    id: 'WO-M1047-01',
    machineId: 'M1047',
    title: 'Emergency Bearing Replacement & Alignment',
    priority: 'EMERGENCY',
    technician: 'Alex Chen (Certified Reliability Tech)',
    scheduledDate: '2026-08-29 17:00 UTC',
    status: 'AWAITING APPROVAL',
    estimatedHours: 2.5,
    requiredParts: ['SKF-6205-2RSH Ball Bearing (Qty 2)', 'Mobilux EP2 Grease'],
  },
  {
    id: 'WO-M4120-02',
    machineId: 'M4120',
    title: 'Radiator Descaling & Coolant Flush',
    priority: 'HIGH',
    technician: 'Maria Rodriguez',
    scheduledDate: '2026-08-30 08:00 UTC',
    status: 'SCHEDULED',
    estimatedHours: 1.5,
    requiredParts: ['Coolant-SYN-50 (5L)', 'Radiator Filter Mesh'],
  },
];

export const MOCK_SHAP_FACTORS = [
  { feature: 'Vibration Harmonic RMS', impact: 31, direction: 'positive', description: 'Radial vibration spike dominates failure risk' },
  { feature: 'Drive Temperature (°C)', impact: 24, direction: 'positive', description: 'Thermal rise above nominal 65°C baseline' },
  { feature: 'Current Variability (A)', impact: 18, direction: 'positive', description: 'Phase torque load imbalance' },
  { feature: 'Total Operating Hours', impact: 11, direction: 'positive', description: 'Approaching 4,000h scheduled inspection' },
  { feature: 'Days Since Last Maintenance', impact: 7, direction: 'positive', description: '12 days elapsed since last lubrication' },
];

export const MOCK_INVESTIGATION_TIMELINE = [
  { step: 'Investigation Initiated', agent: 'Supervisor Agent', time: '14:28:01', status: 'COMPLETED', detail: 'Triggered by vibration breach alert on M1047.' },
  { step: 'Sensor Telemetry Audit', agent: 'Investigator Agent', time: '14:28:02', status: 'COMPLETED', detail: 'Identified +140% vibration surge and +28% thermal rise.' },
  { step: 'Root Cause Diagnostics', agent: 'Root Cause Agent', time: '14:28:03', status: 'COMPLETED', detail: 'Correlated harmonic signature with SKF bearing raceway wear (91% confidence).' },
  { step: 'RAG Knowledge Manual Retrieval', agent: 'Knowledge Agent', time: '14:28:04', status: 'COMPLETED', detail: 'Retrieved SKF Bearing Replacement SOP v3.1 from engineering knowledge base.' },
  { step: 'Work Order Synthesis', agent: 'Maintenance Planner', time: '14:28:05', status: 'COMPLETED', detail: 'Generated Work Order WO-M1047-01 with parts list and 2.5h downtime estimate.' },
  { step: 'Safety & LOTO Verification', agent: 'Verification Agent', time: '14:28:06', status: 'COMPLETED', detail: 'Cleared LOTO isolation protocols & Arc-flash PPE requirements.' },
];
