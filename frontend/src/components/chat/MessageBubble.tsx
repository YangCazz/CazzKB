import { useCallback, useState } from "react";
import type { Message } from "../../types";
import { useStore } from "../../store/chat-store";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeHighlight from "rehype-highlight";
import rehypeRaw from "rehype-raw";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { Check, Copy, Pencil, X, Send, Brain, ChevronDown } from "lucide-react";
import { useCitationComponents } from "../shared/MarkdownComponents";

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

function SourcesPanel({ sources }: { sources: { source: string; header: string; excerpt: string }[] }) {
  if (sources.length === 0) return null;
  return (
    <div className="mt-5 pt-3 border-t" style={{ borderColor: "var(--ds-border-muted)" }}>
      <div className="text-[11px] font-semibold mb-2.5 tracking-wide uppercase" style={{ color: "var(--ds-text-faint)" }}>
        参考来源
      </div>
      <div className="space-y-2">
        {sources.map((s, i) => (
          <div key={i} className="flex gap-2.5 text-[12px] leading-relaxed">
            <span
              className="inline-flex items-center justify-center min-w-[18px] h-[18px] rounded-full text-[10px] font-bold flex-shrink-0 mt-0.5"
              style={{ background: "var(--ds-accent-soft)", color: "var(--ds-accent)" }}
            >
              {i + 1}
            </span>
            <div className="min-w-0">
              <div className="font-medium truncate" style={{ color: "var(--ds-text)" }}>
                {s.source.replace(/\.md$/, "").replace(/-/g, " ")}
                {s.header ? <span className="font-normal ml-1" style={{ color: "var(--ds-text-faint)" }}>› {s.header}</span> : null}
              </div>
              <div className="text-[11px] mt-0.5 line-clamp-2" style={{ color: "var(--ds-text-faint)" }}>
                {s.excerpt}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function AssistantBubble({ msg }: { msg: Message }) {
  const { components, sources } = useCitationComponents();
  const [thinkingOpen, setThinkingOpen] = useState(false);

  return (
    <div className="ds-assistant-message group mb-8">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ background: "var(--ds-accent)" }}>
          <span className="text-[10px] font-bold text-white">K</span>
        </div>
        <span className="text-[13px] font-medium ds-no-select" style={{ color: "var(--ds-text-muted)" }}>CazzKB</span>
        {msg.firstTokenTime != null && (
          <span className="text-[12px] tabular-nums ml-1.5" style={{ color: "var(--ds-text-faint)" }}>
            {msg.firstTokenTime < 1 ? `${Math.round(msg.firstTokenTime * 1000)}ms` : `${msg.firstTokenTime}s`} / {msg.responseTime != null ? (msg.responseTime < 1 ? `${Math.round(msg.responseTime * 1000)}ms` : `${msg.responseTime}s`) : "?"}
          </span>
        )}
      </div>
      <div className="pl-8">
        {msg.thinking && (
          <div className="mb-3 rounded-xl border overflow-hidden" style={{ borderColor: "var(--ds-border-muted)" }}>
            <button
              onClick={() => setThinkingOpen(!thinkingOpen)}
              className="w-full flex items-center gap-2 px-3.5 py-2 text-left transition-colors hover:bg-ds-hover"
              style={{ background: "var(--ds-surface-subtle)" }}
            >
              <Brain className="w-3.5 h-3.5 flex-shrink-0" style={{ color: "var(--ds-accent)" }} />
              <span className="text-[12px] font-medium" style={{ color: "var(--ds-text-muted)" }}>思考过程</span>
              <ChevronDown
                className={`w-3.5 h-3.5 ml-auto flex-shrink-0 transition-transform ${thinkingOpen ? "rotate-180" : ""}`}
                style={{ color: "var(--ds-text-faint)" }}
              />
            </button>
            {thinkingOpen && (
              <div
                className="px-4 py-3 text-[13px] leading-relaxed whitespace-pre-wrap border-t"
                style={{ color: "var(--ds-text-muted)", borderColor: "var(--ds-border-muted)" }}
              >
                {msg.thinking}
              </div>
            )}
          </div>
        )}
        <div className="text-[15px] leading-7" style={{ color: "var(--ds-text)" }}>
          <Markdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeRaw, rehypeHighlight, rehypeKatex]}
            components={components}
          >
            {msg.content}
          </Markdown>
        </div>
        <SourcesPanel sources={sources.current} />
        <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <CopyBtn text={msg.content} />
        </div>
      </div>
    </div>
  );
}
