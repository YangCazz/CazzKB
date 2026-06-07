import { useChat } from "../hooks/useChat";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

interface Props {
  kbId: number | null;
  kbName: string;
}

export default function ChatArea({ kbId, kbName }: Props) {
  const { messages, isStreaming, send, clear } = useChat(kbId);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h2 className="text-sm font-medium text-gray-300">
          {kbName || "Select a knowledge base"}
        </h2>
        {messages.length > 0 && (
          <button
            onClick={clear}
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
          >
            Clear chat
          </button>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            {kbId
              ? "Upload documents and start asking questions."
              : "Create or select a knowledge base to begin."}
          </div>
        ) : (
          messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)
        )}
        {isStreaming && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <span className="animate-pulse">...</span>
          </div>
        )}
      </div>
      <ChatInput onSend={send} disabled={isStreaming || !kbId} />
    </div>
  );
}
