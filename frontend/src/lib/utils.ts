import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Severity } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const SEVERITY_COLOR: Record<Severity, string> = {
  low: "text-blue-400 bg-blue-400/10",
  medium: "text-amber-400 bg-amber-400/10",
  high: "text-orange-400 bg-orange-400/10",
  critical: "text-red-400 bg-red-400/10",
};

export const SEVERITY_BORDER: Record<Severity, string> = {
  low: "border-blue-500/40",
  medium: "border-amber-500/40",
  high: "border-orange-500/40",
  critical: "border-red-500/40",
};

export function riskScoreColor(score: number): string {
  if (score >= 80) return "text-red-400";
  if (score >= 60) return "text-orange-400";
  if (score >= 40) return "text-amber-400";
  return "text-green-400";
}
