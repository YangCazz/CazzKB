import type { ReactNode } from "react";
import { DevBadge } from "../shared/DevBadge";

interface Props { icon: ReactNode; label: string; shortcut?: string; dev?: boolean; onClick?: () => void; }
export function SidebarCommandRow({ icon, label, shortcut, dev, onClick }: Props) {
  return (
    <button onClick={dev ? undefined : onClick}
      className="group w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2.5"
      style={{ background: "transparent" }}
      title={dev ? "正在开发" : undefined}>
      <span className="flex-shrink-0 w-4 h-4 flex items-center justify-center" style={{ color: dev ? "var(--ds-text-faint)" : "var(--ds-text-muted)" }}>{icon}</span>
      <span className="text-[13px] font-medium truncate flex-1" style={{ color: dev ? "var(--ds-text-faint)" : "var(--ds-text-muted)" }}>{label}</span>
      {dev ? <DevBadge /> : shortcut ? <span className="text-[11px] opacity-0 group-hover:opacity-100" style={{ color: "var(--ds-text-faint)" }}>{shortcut}</span> : null}
    </button>
  );
}
