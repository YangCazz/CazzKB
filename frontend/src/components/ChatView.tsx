import { useStore } from "../store/chat-store";
import { MessageTimeline } from "./chat/MessageTimeline";
import { FloatingComposer } from "./chat/FloatingComposer";

export function ChatView() {
  const { selectedKbId, messages, isStreaming, sendMessage, clearChat, kbs } = useStore();
  const kbName = kbs.find((k) => k.id === selectedKbId)?.name || "";

  return (
    <div className="flex flex-col h-full" style={{ background: "var(--ds-bg-canvas)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b" style={{ borderColor: "var(--ds-border-muted)" }}>
        <h2 className="text-[13px] font-medium ds-no-select" style={{ color: "var(--ds-text-muted)" }}>
          {kbName || "选择知识库开始对话"}
        </h2>
        {messages.length > 0 && (
          <button onClick={clearChat} className="text-[12px] transition-colors ds-no-select" style={{ color: "var(--ds-text-faint)" }}>
            清空对话
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <MessageTimeline />
      </div>

      <FloatingComposer onSend={sendMessage} disabled={isStreaming || !selectedKbId} />
    </div>
  );
}
