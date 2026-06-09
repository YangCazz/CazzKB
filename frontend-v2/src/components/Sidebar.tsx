import { useEffect, useState } from "react";
import { useStore } from "../store/chat-store";
import { SidebarFrame } from "./sidebar/SidebarFrame";
import { SidebarSectionHeader } from "./sidebar/SidebarSectionHeader";
import { SidebarTreeRow } from "./sidebar/SidebarTreeRow";
import { SidebarCommandRow } from "./sidebar/SidebarCommandRow";
import { SidebarSearchField } from "./sidebar/SidebarSearchField";
import { FolderKanban, Plus, Upload, Settings, Trash2, MessageSquarePlus } from "lucide-react";

function groupByTime(items: { id: number; title: string; created_at: string; message_count: number }[]) {
  const now = Date.now();
  const t = new Date(); t.setHours(0, 0, 0, 0); const today = t.getTime();
  const yesterday = today - 86400000;
  const week = today - new Date().getDay() * 86400000;
  const groups: [string, typeof items][] = [["今天", []], ["昨天", []], ["本周", []], ["更早", []]];
  for (const c of items) { const ts = new Date(c.created_at).getTime(); if (ts >= today) groups[0][1].push(c); else if (ts >= yesterday) groups[1][1].push(c); else if (ts >= week) groups[2][1].push(c); else groups[3][1].push(c); }
  return groups.filter(([, v]) => v.length > 0);
}

export function Sidebar() {
  const { kbs, selectedKbId, conversations, activeConvId, loadKBs, selectKB, createKB, deleteKB, uploadDoc, loadConversations, selectConversation, deleteConversation, clearChat } = useStore();
  const [convSearch, setConvSearch] = useState("");

  useEffect(() => { loadKBs(); }, [loadKBs]);
  useEffect(() => { loadConversations(); }, [loadConversations, selectedKbId]);

  const filteredConvs = convSearch ? conversations.filter((c) => c.title.toLowerCase().includes(convSearch.toLowerCase())) : conversations;
  const groups = groupByTime(filteredConvs);

  return (
    <SidebarFrame>
      {/* Brand + New Chat */}
      <div className="px-4 py-3.5 border-b flex items-center justify-between" style={{ borderColor: "var(--ds-border-muted)" }}>
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0" style={{ background: "var(--ds-accent)" }}>
            <span className="text-[11px] font-bold text-white">K</span>
          </div>
          <span className="text-[15px] font-semibold select-none" style={{ color: "var(--ds-text)" }}>CazzKB</span>
        </div>
        <button onClick={clearChat} className="p-1 rounded-md transition-colors hover:bg-ds-hover" style={{ color: "var(--ds-text-muted)" }} title="新对话">
          <MessageSquarePlus className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-1.5">
        {/* KB Section */}
        <SidebarSectionHeader label="知识库" />
        {kbs.map((kb) => (
          <SidebarTreeRow key={kb.id} icon={<FolderKanban className="w-3.5 h-3.5" />} label={kb.name} subtitle={`${kb.chunk_count} 个分块`}
            active={selectedKbId === kb.id} onClick={() => selectKB(kb.id)}
            actions={
              <button onClick={(e) => { e.stopPropagation(); if (confirm("删除该知识库？")) deleteKB(kb.id); }} style={{ color: "var(--ds-text-faint)" }}>
                <Trash2 className="w-3 h-3" />
              </button>
            } />
        ))}

        {/* Command rows */}
        <div className="mt-1 pt-1 border-t mx-3" style={{ borderColor: "var(--ds-border-muted)" }} />
        <SidebarCommandRow icon={<Plus className="w-4 h-4" />} label="新建知识库" shortcut="Ctrl+N" onClick={async () => { const n = prompt("知识库名称:"); if (n) await createKB(n); }} />
        <SidebarCommandRow icon={<Upload className="w-4 h-4" />} label="上传文档" onClick={() => { if (!selectedKbId) return; const i = document.createElement("input"); i.type = "file"; i.accept = ".md,.txt"; i.onchange = (e) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) uploadDoc(f); }; i.click(); }} />
        <SidebarCommandRow icon={<Settings className="w-4 h-4" />} label="设置" dev shortcut="Ctrl+," />

        {/* Conversations Section */}
        {selectedKbId ? (
          <>
            <div className="mt-2 pt-2 border-t mx-3" style={{ borderColor: "var(--ds-border-muted)" }} />
            <SidebarSectionHeader label="对话历史" />
            <SidebarSearchField value={convSearch} onChange={setConvSearch} />
            {groups.length === 0 ? (
              <p className="px-3 py-6 text-center text-[13px] select-none" style={{ color: "var(--ds-text-faint)" }}>
                {convSearch ? "无匹配对话" : "暂无对话记录"}
              </p>
            ) : (
              groups.map(([label, items]) => (
                <div key={label} className="mb-1">
                  <div className="px-3 py-1 text-[11px] font-medium select-none" style={{ color: "var(--ds-text-faint)" }}>{label}</div>
                  {items.map((c) => (
                    <SidebarTreeRow key={c.id} label={c.title} subtitle={`${c.message_count} 条消息`}
                      active={activeConvId === c.id} onClick={() => selectConversation(c.id)}
                      actions={<button onClick={(e) => { e.stopPropagation(); deleteConversation(c.id); }} style={{ color: "var(--ds-text-faint)" }}><Trash2 className="w-3 h-3" /></button>} />
                  ))}
                </div>
              ))
            )}
          </>
        ) : null}
      </div>
    </SidebarFrame>
  );
}
