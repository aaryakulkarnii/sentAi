// ── Alert ────────────────────────────────────────────────────────────────────
export type Severity = "low" | "medium" | "high" | "critical";
export type AlertStatus = "open" | "investigating" | "resolved" | "false_positive";

export interface Alert {
  id: string;
  severity: Severity;
  confidence: number;
  source_ip: string | null;
  dest_ip: string | null;
  description: string | null;
  mitre_technique_id: string | null;
  status: AlertStatus;
  created_at: string;
}

// ── Incident ─────────────────────────────────────────────────────────────────
export type IncidentStatus = "open" | "investigating" | "contained" | "resolved" | "closed";

export interface Incident {
  id: string;
  title: string;
  description: string | null;
  status: IncidentStatus;
  risk_score: number;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

// ── Investigation ─────────────────────────────────────────────────────────────
export interface TimelineEvent {
  timestamp: string;
  technique_id: string | null;
  description: string | null;
  source_ip: string | null;
  severity: string;
}

export interface Investigation {
  id: string;
  incident_id: string;
  risk_score: number;
  attack_timeline: TimelineEvent[];
  mitre_mappings: Record<string, string[]>;
  iocs: Record<string, string[]>;
  remediation: Record<string, string[]>;
  created_at: string;
}

export interface IncidentDetail extends Incident {
  alert_count: number;
  technique_ids: string[];
}

export interface IncidentNote {
  id: string;
  incident_id: string;
  author_id: string;
  content: string;
  created_at: string;
}

// ── Asset ─────────────────────────────────────────────────────────────────────
export interface Asset {
  id: string;
  hostname: string;
  ip: string | null;
  os: string | null;
  criticality: number; // 1–5
  owner: string | null;
  created_at: string;
}

// ── MITRE ─────────────────────────────────────────────────────────────────────
export interface MitreTechnique {
  id: string;           // T1059.001
  tactic: string;
  technique: string;
  sub_technique: string | null;
  description: string | null;
  url: string | null;
}

export interface MatrixTechnique {
  id: string;
  technique: string;
  sub_technique: string | null;
  covered: boolean;
  alert_count: number;
}

export interface MatrixTactic {
  id: string | null;
  name: string;
  techniques: MatrixTechnique[];
  alert_count: number;
}

export interface MitreMatrix {
  tactics: MatrixTactic[];
  total_techniques: number;
  covered_techniques: number;
}

// ── User ─────────────────────────────────────────────────────────────────────
export type UserRole = "tier1" | "tier2" | "manager" | "engineer";

export interface User {
  id: string;
  email: string;
  role: UserRole;
}
