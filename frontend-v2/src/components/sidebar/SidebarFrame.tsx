import type { ReactNode } from "react";

export function SidebarFrame({ children, width = 268 }: { children: ReactNode; width?: number }) {
  return (
    <aside className="flex flex-col h-full border-r overflow-hidden select-none"
      style={{ width, minWidth: width, background: "var(--ds-bg-sidebar)", borderColor: "var(--ds-border-muted)" }}>
      {children}
    </aside>
  );
}
