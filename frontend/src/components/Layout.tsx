import type { ReactNode } from "react";

export default function Layout({
  sidebar,
  main,
}: {
  sidebar: ReactNode;
  main: ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-950">
      <aside className="w-64 flex-shrink-0 border-r border-gray-800 bg-gray-900 flex flex-col">
        {sidebar}
      </aside>
      <main className="flex-1 flex flex-col min-w-0">{main}</main>
    </div>
  );
}
