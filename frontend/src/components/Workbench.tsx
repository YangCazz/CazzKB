import { useEffect } from "react";
import { useStore } from "../store/chat-store";
import { Sidebar } from "./Sidebar";
import { ChatView } from "./ChatView";

export function Workbench() {
  const loadKBs = useStore((s) => s.loadKBs);
  useEffect(() => { loadKBs(); }, [loadKBs]);

  return (
    <div className="flex h-screen" style={{ background: "var(--ds-bg-main)" }}>
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <ChatView />
      </div>
    </div>
  );
}
