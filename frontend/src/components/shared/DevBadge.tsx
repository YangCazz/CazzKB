import { Construction } from "lucide-react";

export function DevBadge({ label = "开发中" }: { label?: string }) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium cursor-help select-none"
      style={{ background: "var(--ds-surface-subtle)", color: "var(--ds-text-faint)" }}
      title="此功能正在开发中，敬请期待"
    >
      <Construction className="w-3 h-3" />
      {label}
    </span>
  );
}
