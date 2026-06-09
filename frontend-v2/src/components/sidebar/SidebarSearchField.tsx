import { Search, X } from "lucide-react";

interface Props { value: string; onChange: (v: string) => void; placeholder?: string; }
export function SidebarSearchField({ value, onChange, placeholder = "搜索对话..." }: Props) {
  return (
    <div className="px-3 py-1.5">
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border" style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border)" }}>
        <Search className="w-3.5 h-3.5 flex-shrink-0" style={{ color: "var(--ds-text-faint)" }} />
        <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
          className="flex-1 bg-transparent text-[13px] outline-none" style={{ color: "var(--ds-text)" }} />
        {value ? <button onClick={() => onChange("")} className="flex-shrink-0"><X className="w-3.5 h-3.5" style={{ color: "var(--ds-text-faint)" }} /></button> : null}
      </div>
    </div>
  );
}
