import { useRef, useEffect } from "react";
import { useStore } from "../../store/chat-store";
import { UserBubble, AssistantBubble } from "./MessageBubble";
import { ChatStarterGrid } from "./ChatStarterGrid";
import { Loader2 } from "lucide-react";

export function MessageTimeline() {
  const { messages, isStreaming, selectedKbId, sendMessage } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  return (
    <div className="max-w-[860px] mx-auto px-8 py-8">
      {messages.length === 0 ? (
        selectedKbId ? <ChatStarterGrid onSelect={sendMessage} /> : (
          <div className="flex items-center justify-center py-32">
            <p className="text-[15px] select-none" style={{ color: "var(--ds-text-faint)" }}>创建或选择一个知识库</p>
          </div>
        )
      ) : (
        <>
          {messages.map((msg, i) =>
            msg.role === "user"
              ? <UserBubble key={i} msg={msg} index={i} />
              : <AssistantBubble key={i} msg={msg} />
          )}
          {isStreaming && <div className="flex items-center gap-2 pl-8 mt-2" style={{ color: "var(--ds-text-faint)" }}><Loader2 className="w-4 h-4 animate-spin" /></div>}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
