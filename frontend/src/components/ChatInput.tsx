import { useState, type FormEvent, useRef, useEffect } from "react";
import { ArrowUp } from "lucide-react";

interface Props {
  onSend: (q: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { if (!disabled) ref.current?.focus(); }, [disabled]);

  const submit = (e?: FormEvent) => {
    e?.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value); setValue("");
  };

  return (
    <div className="px-6 pb-5 pt-2" style={{ background: "var(--ds-bg-canvas)" }}>
      <form
        onSubmit={submit}
        className="flex items-end gap-3 max-w-[860px] mx-auto p-2.5 rounded-[22px] border shadow-composer transition-colors"
        style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border)" }}
      >
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px";
          }}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
          placeholder="输入你的问题... (Enter 发送, Shift+Enter 换行)"
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none bg-transparent text-[15px] leading-[1.58] font-medium outline-none disabled:opacity-30"
          style={{ color: "var(--ds-text)" }}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="flex-shrink-0 h-9 w-9 rounded-full flex items-center justify-center transition-all disabled:opacity-30"
          style={{ background: value.trim() && !disabled ? "var(--ds-accent)" : "var(--ds-surface-subtle)", color: value.trim() && !disabled ? "white" : "var(--ds-text-faint)" }}
        >
          <ArrowUp className="w-4 h-4" strokeWidth={2.5} />
        </button>
      </form>
    </div>
  );
}
