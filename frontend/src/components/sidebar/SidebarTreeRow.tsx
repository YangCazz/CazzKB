import type { ReactNode } from "react";

interface Props {
  icon?: ReactNode; label: string; subtitle?: string; active?: boolean; actions?: ReactNode; onClick?: () => void;
}
export function SidebarTreeRow({ icon, label, subtitle, active, actions, onClick }: Props) {
  return (
    <button onClick={onClick} className="group w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2.5"
      style={{ background: active ? "var(--ds-accent-soft)" : "transparent" }}>
      {icon ? <span className="flex-shrink-0 w-4 h-4 flex items-center justify-center" style={{ color: active ? "var(--ds-accent)" : "var(--ds-text-muted)" }}>{icon}</span> : null}
      <div className="min-w-0 flex-1">
        <div className="text-[13px] font-medium truncate" style={{ color: active ? "var(--ds-accent)" : "var(--ds-text-muted)" }}>{label}</div>
        {subtitle ? <div className="text-[11px] mt-0.5" style={{ color: "var(--ds-text-faint)" }}>{subtitle}</div> : null}
      </div>
      {actions ? <span className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">{actions}</span> : null}
    </button>
  );
}
