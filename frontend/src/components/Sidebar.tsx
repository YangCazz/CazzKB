import { useState, useEffect } from "react";
import { listKBs, createKB, deleteKB, uploadDocument } from "../api/client";
import type { KnowledgeBase } from "../types";

interface Props {
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export default function Sidebar({ selectedId, onSelect }: Props) {
  const [kbs, setKBs] = useState<KnowledgeBase[]>([]);

  const load = async () => {
    try {
      setKBs(await listKBs());
    } catch {}
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    const name = prompt("Knowledge base name:");
    if (!name) return;
    const kb = await createKB(name);
    setKBs((prev) => [...prev, kb]);
    onSelect(kb.id);
  };

  const handleUpload = async () => {
    if (!selectedId) return;
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".md,.txt,.markdown";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      await uploadDocument(selectedId, file);
      load();
    };
    input.click();
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Delete "${name}"?`)) return;
    await deleteKB(id);
    if (selectedId === id) onSelect(0);
    load();
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-lg font-bold text-cyan-400">CazzKB</h1>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {kbs.map((kb) => (
          <div
            key={kb.id}
            className={`group flex items-center gap-2 p-3 rounded-lg text-sm transition-colors cursor-pointer ${
              selectedId === kb.id
                ? "bg-cyan-900/40 text-cyan-200 border border-cyan-800"
                : "hover:bg-gray-800 text-gray-300"
            }`}
            onClick={() => onSelect(kb.id)}
          >
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{kb.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">
                {kb.chunk_count} chunks
              </div>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); handleDelete(kb.id, kb.name); }}
              className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all text-xs p-1"
              title="Delete knowledge base"
            >
              X
            </button>
          </div>
        ))}
      </div>
      <div className="p-3 border-t border-gray-800 space-y-2">
        <button
          onClick={handleCreate}
          className="w-full py-2 text-sm bg-cyan-700 hover:bg-cyan-600 rounded-lg transition-colors"
        >
          + New KB
        </button>
        {selectedId ? (
          <button
            onClick={handleUpload}
            className="w-full py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            Upload Document
          </button>
        ) : null}
      </div>
    </div>
  );
}
