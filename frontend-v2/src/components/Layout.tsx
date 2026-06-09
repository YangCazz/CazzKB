import type { ReactNode } from "react";

export function Layout({ sidebar, main }: { sidebar: ReactNode; main: ReactNode }) {
  return (
    <div className="flex h-screen" style={{ background: "var(--ds-bg-main)" }}>
      <aside className="w-80 flex-shrink-0 border-r flex flex-col" style={{ background: "var(--ds-bg-sidebar)", borderColor: "var(--ds-border-muted)" }}>
        {sidebar}
      </aside>
      <main className="flex-1 flex flex-col min-w-0" style={{ background: "var(--ds-bg-canvas)" }}>
        {main}
      </main>
    </div>
  );
}
