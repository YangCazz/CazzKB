import { useCallback, useState } from "react";
import type { Message } from "../../types";
import { useStore } from "../../store/chat-store";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Check, Copy, Pencil, X, Send } from "lucide-react";
import { sharedMdComponents } from "../shared/MarkdownComponents";

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  const cp = useCallback(() => {
    navigator.clipboard.writeText(text);
    setOk(true); setTimeout(() => setOk(false), 1600);
  }, [text]);
  return (
    <button onClick={cp} className="p-1 rounded-md transition-colors hover:bg-ds-hover" style={{ color: "var(--ds-text-faint)" }}>
      {ok ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

export function UserBubble({ msg, index }: { msg: Message; index: number }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(msg.content);

  const handleEdit = () => {
    setDraft(msg.content);
    setEditing(true);
  };

  const handleCancel = () => {
    setEditing(false);
    setDraft(msg.content);
  };

  const handleResend = () => {
    if (!draft.trim()) return;
    setEditing(false);
    useStore.getState().editMessage(index, draft);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      handleCancel();
    }
  };

  if (editing) {
    return (
      <div className="ds-user-message flex justify-end mb-8 pr-1">
        <div className="min-w-0 max-w-[75%]">
          <textarea
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full resize-none text-[15px] leading-[1.58] font-medium p-4 rounded-[22px] outline-none border-2"
            style={{
              background: "var(--ds-bubble-user)",
              color: "var(--ds-bubble-user-fg)",
              borderColor: "var(--ds-accent)",
            }}
            rows={3}
          />
          <div className="mt-2 flex items-center justify-end gap-2">
            <button
              onClick={handleCancel}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[13px] font-medium transition-colors"
              style={{ background: "var(--ds-surface-subtle)", color: "var(--ds-text-muted)" }}
            >
              <X className="w-3.5 h-3.5" />
              取消
            </button>
            <button
              onClick={handleResend}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-[13px] font-medium transition-colors"
              style={{ background: "var(--ds-accent)", color: "#fff" }}
            >
              <Send className="w-3.5 h-3.5" />
              重新发送
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ds-user-message group flex justify-end mb-8 pr-1">
      <div className="min-w-0 max-w-[75%]">
        <div className="whitespace-pre-wrap break-words text-[15px] leading-[1.58] font-medium px-5 py-3 rounded-[22px]"
          style={{ background: "var(--ds-bubble-user)", color: "var(--ds-bubble-user-fg)" }}>
          {msg.content}
        </div>
        <div className="mt-1.5 flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleEdit}
            className="p-1 rounded-md transition-colors hover:bg-ds-hover"
            style={{ color: "var(--ds-text-faint)" }}
            title="编辑"
          >
            <Pencil className="w-4 h-4" />
          </button>
          <CopyBtn text={msg.content} />
        </div>
      </div>
    </div>
  );
}

export function AssistantBubble({ msg }: { msg: Message }) {
  return (
    <div className="ds-assistant-message group mb-8">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "var(--ds-accent)" }}>
          <span className="text-[10px] font-bold text-white">K</span>
        </div>
        <span className="text-[13px] font-medium ds-no-select" style={{ color: "var(--ds-text-muted)" }}>CazzKB</span>
        {msg.responseTime != null && (
          <span className="text-[12px] tabular-nums ml-1.5" style={{ color: "var(--ds-text-faint)" }}>
            {msg.responseTime < 1 ? `${Math.round(msg.responseTime * 1000)}ms` : `${msg.responseTime}s`}
          </span>
        )}
      </div>
      <div className="pl-8">
        <div className="text-[15px] leading-7" style={{ color: "var(--ds-text)" }}>
          <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]} components={sharedMdComponents}>
            {msg.content}
          </Markdown>
        </div>
        <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyBtn text={msg.content} />
        </div>
      </div>
    </div>
  );
}
