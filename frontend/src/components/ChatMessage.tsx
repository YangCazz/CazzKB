import type { ChatMessage as ChatMessageType } from "../types";

export default function ChatMessage({ msg }: { msg: ChatMessageType }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-xl px-4 py-3 ${
          isUser
            ? "bg-cyan-700 text-white"
            : "bg-gray-800 text-gray-100"
        }`}
      >
        <div className="text-xs mb-1 opacity-60">
          {isUser ? "You" : "CazzKB"}
        </div>
        <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap">
          {msg.content}
        </div>
      </div>
    </div>
  );
}
