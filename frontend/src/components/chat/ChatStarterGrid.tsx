import { Lightbulb, BookOpen, FileText } from "lucide-react";

interface Props { onSelect: (prompt: string) => void; }
export function ChatStarterGrid({ onSelect }: Props) {
  const cards = [
    { icon: <BookOpen className="w-5 h-5" />, title: "结构化回答", desc: "请用结构化方式回答我的问题，包含要点和总结", color: "#0088ff", bg: "rgba(0,136,255,0.06)" },
    { icon: <Lightbulb className="w-5 h-5" />, title: "技术解释", desc: "深入解释一个技术概念，包含原理和应用场景", color: "#128a4a", bg: "rgba(18,138,74,0.06)" },
    { icon: <FileText className="w-5 h-5" />, title: "总结文档", desc: "总结知识库中的相关文档要点", color: "#7c3aed", bg: "rgba(124,58,237,0.06)" },
  ];
  return (
    <div className="grid grid-cols-1 gap-4 max-w-[520px] mx-auto py-12">
      {cards.map((c, i) => (
        <button key={i} onClick={() => onSelect(c.desc)}
          className="flex items-start gap-4 p-5 rounded-2xl border text-left transition-all hover:shadow-card-strong"
          style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border-muted)" }}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: c.bg, color: c.color }}>{c.icon}</div>
          <div>
            <div className="text-[15px] font-semibold" style={{ color: "var(--ds-text)" }}>{c.title}</div>
            <div className="text-[13px] mt-1" style={{ color: "var(--ds-text-muted)" }}>{c.desc}</div>
          </div>
        </button>
      ))}
    </div>
  );
}
