import { BookOpen, FileText, Sparkles } from "lucide-react";
import { useEffect } from "react";
import { useStore } from "../store/chat-store";

const artifactLabels: Record<string, string> = {
  note: "笔记",
  briefing: "简报",
  faq: "FAQ",
  study_guide: "学习指南",
  timeline: "时间线",
  mind_map: "思维导图",
};

export function NotebookPanel() {
  const { selectedKbId, sources, artifacts, loadNotebookAssets, createArtifact } = useStore();

  useEffect(() => { loadNotebookAssets(); }, [loadNotebookAssets, selectedKbId]);

  const handleCreateNote = async () => {
    if (!selectedKbId) return;
    const title = prompt("Artifact 标题:", "研究笔记");
    if (!title) return;
    const content = prompt("先写入一段内容，之后我们会接入 AI 自动生成:", "");
    if (content === null) return;
    await createArtifact({ title, artifact_type: "note", content, metadata: { source_ids: [] } });
  };

  return (
    <aside
      className="hidden xl:flex w-80 flex-shrink-0 border-l flex-col"
      style={{ background: "var(--ds-bg-sidebar)", borderColor: "var(--ds-border-muted)" }}
    >
      <div className="px-4 py-3.5 border-b" style={{ borderColor: "var(--ds-border-muted)" }}>
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4" style={{ color: "var(--ds-accent)" }} />
          <h2 className="text-[14px] font-semibold" style={{ color: "var(--ds-text)" }}>Notebook</h2>
        </div>
        <p className="mt-1 text-[12px]" style={{ color: "var(--ds-text-faint)" }}>
          资料源、笔记与后续 Studio 输出会在这里汇总。
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {!selectedKbId ? (
          <p className="text-[13px] leading-6 text-center py-10" style={{ color: "var(--ds-text-faint)" }}>
            选择一个知识库后查看资料源与 Artifacts。
          </p>
        ) : (
          <>
            <section>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-[12px] font-semibold uppercase tracking-wide" style={{ color: "var(--ds-text-muted)" }}>
                  Sources · {sources.length}
                </h3>
              </div>
              <div className="space-y-2">
                {sources.length === 0 ? (
                  <EmptyCard text="还没有资料源。先上传 Markdown 或文本文件。" />
                ) : (
                  sources.map((source) => (
                    <div
                      key={source.id}
                      className="rounded-xl border p-3"
                      style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border-muted)" }}
                    >
                      <div className="flex items-start gap-2">
                        <FileText className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: "var(--ds-text-faint)" }} />
                        <div className="min-w-0">
                          <p className="text-[13px] font-medium truncate" style={{ color: "var(--ds-text)" }}>
                            {source.title}
                          </p>
                          <p className="text-[11px] mt-0.5" style={{ color: "var(--ds-text-faint)" }}>
                            {source.chunk_count} chunks · {source.source_type}
                          </p>
                          {source.summary ? (
                            <p className="text-[12px] mt-2 line-clamp-3" style={{ color: "var(--ds-text-muted)" }}>
                              {source.summary}
                            </p>
                          ) : null}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-[12px] font-semibold uppercase tracking-wide" style={{ color: "var(--ds-text-muted)" }}>
                  Studio · {artifacts.length}
                </h3>
                <button
                  onClick={handleCreateNote}
                  className="text-[12px] rounded-lg px-2 py-1 transition-colors"
                  style={{ background: "var(--ds-accent-soft)", color: "var(--ds-accent)" }}
                >
                  新建
                </button>
              </div>
              <div className="space-y-2">
                {artifacts.length === 0 ? (
                  <EmptyCard text="还没有 Artifact。下一步可生成简报、FAQ、学习指南。" />
                ) : (
                  artifacts.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="rounded-xl border p-3"
                      style={{ background: "var(--ds-surface-card)", borderColor: "var(--ds-border-muted)" }}
                    >
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: "var(--ds-accent)" }} />
                        <div className="min-w-0">
                          <p className="text-[13px] font-medium truncate" style={{ color: "var(--ds-text)" }}>
                            {artifact.title}
                          </p>
                          <p className="text-[11px] mt-0.5" style={{ color: "var(--ds-text-faint)" }}>
                            {artifactLabels[artifact.artifact_type] ?? artifact.artifact_type}
                          </p>
                          <p className="text-[12px] mt-2 line-clamp-4 whitespace-pre-wrap" style={{ color: "var(--ds-text-muted)" }}>
                            {artifact.content}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </aside>
  );
}

function EmptyCard({ text }: { text: string }) {
  return (
    <div
      className="rounded-xl border border-dashed p-4 text-[12px] leading-5"
      style={{ color: "var(--ds-text-faint)", borderColor: "var(--ds-border-muted)" }}
    >
      {text}
    </div>
  );
}
