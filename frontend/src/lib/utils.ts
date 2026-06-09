import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Severity } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Severity → badge classes. Color is reserved strictly for these semantics;
// kept low-saturation so it reads premium against the monochrome base.
export const SEVERITY_COLOR: Record<Severity, string> = {
  low: "text-sev-low bg-sev-low/10 ring-1 ring-inset ring-sev-low/20",
  medium: "text-sev-medium bg-sev-medium/10 ring-1 ring-inset ring-sev-medium/20",
  high: "text-sev-high bg-sev-high/10 ring-1 ring-inset ring-sev-high/20",
  critical: "text-sev-critical bg-sev-critical/10 ring-1 ring-inset ring-sev-critical/20",
};

export const SEVERITY_DOT: Record<Severity, string> = {
  low: "bg-sev-low",
  medium: "bg-sev-medium",
  high: "bg-sev-high",
  critical: "bg-sev-critical",
};

export const STATUS_COLOR: Record<string, string> = {
  open: "text-sev-critical bg-sev-critical/10 ring-1 ring-inset ring-sev-critical/20",
  investigating: "text-sev-medium bg-sev-medium/10 ring-1 ring-inset ring-sev-medium/20",
  contained: "text-sev-low bg-sev-low/10 ring-1 ring-inset ring-sev-low/20",
  resolved: "text-sev-ok bg-sev-ok/10 ring-1 ring-inset ring-sev-ok/20",
  closed: "text-ink-300 bg-white/[0.04] ring-1 ring-inset ring-white/10",
  false_positive: "text-ink-300 bg-white/[0.04] ring-1 ring-inset ring-white/10",
};

export function riskScoreColor(score: number): string {
  if (score >= 80) return "text-sev-critical";
  if (score >= 60) return "text-sev-high";
  if (score >= 40) return "text-sev-medium";
  return "text-sev-ok";
}

export function riskScoreLabel(score: number): string {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}
