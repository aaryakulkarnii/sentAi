"use client";

import { forwardRef, type ButtonHTMLAttributes, type HTMLAttributes, type ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/* ── Panel ─────────────────────────────────────────────────────────────────── */
export function Panel({
  className,
  hover,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement> & { hover?: boolean }) {
  return (
    <div className={cn("panel", hover && "panel-hover", className)} {...props}>
      <div className="relative">{children}</div>
    </div>
  );
}

/* ── PageHeader ────────────────────────────────────────────────────────────── */
export function PageHeader({
  title,
  subtitle,
  icon,
  actions,
}: {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex items-start gap-3">
        {icon && (
          <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] text-ink-100">
            {icon}
          </div>
        )}
        <div>
          <h1 className="text-[1.35rem] font-semibold tracking-tightest text-white">{title}</h1>
          {subtitle && <p className="mt-0.5 text-sm text-ink-300">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

/* ── Badge ─────────────────────────────────────────────────────────────────── */
export function Badge({
  className,
  children,
  dot,
}: {
  className?: string;
  children: ReactNode;
  dot?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium capitalize",
        className,
      )}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dot)} />}
      {children}
    </span>
  );
}

/* ── Button ────────────────────────────────────────────────────────────────── */
type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
  loading?: boolean;
};

const BTN_VARIANTS: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-white text-ink-950 hover:bg-ink-100 shadow-[0_1px_2px_rgba(0,0,0,0.4)] disabled:opacity-50",
  secondary:
    "border border-white/10 bg-white/[0.04] text-ink-100 hover:bg-white/[0.08] hover:border-white/20 disabled:opacity-50",
  ghost: "text-ink-200 hover:bg-white/[0.06] hover:text-white disabled:opacity-40",
  danger:
    "border border-sev-critical/30 bg-sev-critical/10 text-sev-critical hover:bg-sev-critical/20 disabled:opacity-50",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "secondary", size = "md", loading, children, disabled, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150 outline-none focus-visible:ring-2 focus-visible:ring-white/30 disabled:cursor-not-allowed",
        size === "sm" ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm",
        BTN_VARIANTS[variant],
        className,
      )}
      {...props}
    >
      {loading && <Loader2 size={size === "sm" ? 13 : 15} className="animate-spin" />}
      {children}
    </button>
  );
});

/* ── Input ─────────────────────────────────────────────────────────────────── */
export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...props }, ref) {
    return (
      <input
        ref={ref}
        className={cn(
          "w-full rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5 text-sm text-white placeholder:text-ink-400 outline-none transition-colors focus:border-white/25 focus:bg-white/[0.05]",
          className,
        )}
        {...props}
      />
    );
  },
);

/* ── StatCard ──────────────────────────────────────────────────────────────── */
export function StatCard({
  label,
  value,
  sub,
  accent,
  index = 0,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
  index?: number;
}) {
  return (
    <div
      className="panel panel-hover animate-fade-up p-5"
      style={{ animationDelay: `${index * 60}ms`, animationFillMode: "backwards" }}
    >
      <div className="relative">
        <p className="text-[0.7rem] font-medium uppercase tracking-wider text-ink-400">{label}</p>
        <p className={cn("mt-2 font-mono text-3xl font-semibold tabular-nums text-white", accent)}>
          {value}
        </p>
        {sub && <p className="mt-1 text-xs text-ink-400">{sub}</p>}
      </div>
    </div>
  );
}

/* ── EmptyState ────────────────────────────────────────────────────────────── */
export function EmptyState({
  icon,
  title,
  hint,
}: {
  icon?: ReactNode;
  title: string;
  hint?: ReactNode;
}) {
  return (
    <div className="dot-grid flex flex-col items-center justify-center rounded-xl border border-dashed border-white/10 px-6 py-16 text-center">
      {icon && (
        <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-ink-300">
          {icon}
        </div>
      )}
      <p className="text-sm font-medium text-ink-200">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-xs text-ink-400">{hint}</p>}
    </div>
  );
}

/* ── Skeleton ──────────────────────────────────────────────────────────────── */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton h-4 w-full", className)} />;
}
