import type { ReactNode } from "react";

export function SidebarSectionHeader({ label, actions }: { label: string; actions?: ReactNode }) {
  return (
    <div className="flex items-center justify-between px-3 py-1.5">
      <span className="text-[11px] font-semibold uppercase tracking-wider select-none" style={{ color: "var(--ds-text-faint)" }}>{label}</span>
      {actions}
    </div>
  );
}
