import { ListTodo } from "lucide-react";
import { DevBadge } from "../shared/DevBadge";

export function ReviewPlanCard() {
  return (
    <div className="flex min-h-[64px] w-full items-center gap-3 rounded-[18px] border px-4 py-3 my-3 opacity-60 cursor-not-allowed select-none"
      style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border-muted)", boxShadow: "var(--ds-shadow-card-soft)" }}>
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full" style={{ background: "var(--ds-surface-subtle)" }}>
        <ListTodo className="h-5 w-5" style={{ color: "var(--ds-text-faint)" }} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-[14.5px] font-semibold" style={{ color: "var(--ds-text-muted)" }}>任务计划</span>
          <DevBadge />
        </div>
        <div className="mt-0.5 text-[12.5px]" style={{ color: "var(--ds-text-faint)" }}>Agent 任务计划和执行步骤将在此显示</div>
      </div>
    </div>
  );
}
