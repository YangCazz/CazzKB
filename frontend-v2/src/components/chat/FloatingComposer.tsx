import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { ArrowUp, Atom } from "lucide-react";
import { DevBadge } from "../shared/DevBadge";

interface Props { onSend: (q: string) => void; disabled: boolean; }
export function FloatingComposer({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { if (!disabled) ref.current?.focus(); }, [disabled]);

  const submit = () => { if (!value.trim() || disabled) return; onSend(value.trim()); setValue(""); };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey) { e.preventDefault(); submit(); }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); setValue((v) => v + "\n"); }
  };

  return (
    <div className="px-6 pb-5 pt-2" style={{ background: "var(--ds-bg-canvas)" }}>
      <form onSubmit={(e) => { e.preventDefault(); submit(); }}
        className="flex items-end gap-3 max-w-[860px] mx-auto p-2.5 rounded-[22px] border shadow-composer transition-colors"
        style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border)" }}>
        <button type="button" disabled className="flex-shrink-0 h-9 w-9 rounded-full flex items-center justify-center opacity-50"
          style={{ background: "var(--ds-surface-subtle)", color: "var(--ds-text-faint)" }} title="模型切换 - 开发中">
          <Atom className="w-4 h-4" />
        </button>
        <textarea ref={ref} value={value}
          onChange={(e) => { setValue(e.target.value); e.target.style.height = "auto"; e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px"; }}
          onKeyDown={handleKeyDown}
          placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
          disabled={disabled} rows={1}
          className="flex-1 resize-none bg-transparent text-[15px] leading-[1.58] font-medium outline-none disabled:opacity-30"
          style={{ color: "var(--ds-text)" }} />
        <button type="submit" disabled={disabled || !value.trim()}
          className="flex-shrink-0 h-9 w-9 rounded-full flex items-center justify-center transition-all disabled:opacity-30"
          style={{ background: value.trim() && !disabled ? "var(--ds-accent)" : "var(--ds-surface-subtle)", color: value.trim() && !disabled ? "white" : "var(--ds-text-faint)" }}>
          <ArrowUp className="w-4 h-4" strokeWidth={2.5} />
        </button>
      </form>
      <div className="flex items-center justify-between max-w-[860px] mx-auto mt-1.5 px-3">
        <span className="text-[11px] select-none" style={{ color: "var(--ds-text-faint)" }}>CazzKB 可能会出错，请核实重要信息</span>
        <DevBadge label="更多功能开发中" />
      </div>
    </div>
  );
}
