import type { KnowledgeBase, Conversation, Message } from "../types";

const BASE = "/api";

// --- KB ---
export async function listKBs(): Promise<KnowledgeBase[]> {
  const r = await fetch(`${BASE}/kb`); return r.json();
}
export async function createKB(name: string, desc = ""): Promise<KnowledgeBase> {
  const r = await fetch(`${BASE}/kb`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, description: desc }) });
  return r.json();
}
export async function deleteKB(id: number): Promise<void> {
  await fetch(`${BASE}/kb/${id}`, { method: "DELETE" });
}
export async function uploadDocument(kbId: number, file: File): Promise<Document> {
  const fd = new FormData(); fd.append("file", file);
  const r = await fetch(`${BASE}/kb/${kbId}/upload`, { method: "POST", body: fd });
  return r.json();
}

// --- Conversations ---
export async function listConversations(kbId: number): Promise<Conversation[]> {
  const r = await fetch(`${BASE}/kb/${kbId}/conversations`); return r.json();
}
export async function getConversation(id: number): Promise<{ id: number; title: string; messages: { role: string; content: string; sources: string; created_at: string }[] }> {
  const r = await fetch(`${BASE}/conversations/${id}`);
  if (!r.ok) throw new Error("Not found");
  return r.json();
}
export async function deleteConversation(id: number): Promise<void> {
  await fetch(`${BASE}/conversations/${id}`, { method: "DELETE" });
}

export async function renameConversation(id: number, title: string): Promise<void> {
  await fetch(`${BASE}/conversations/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
}

// --- Chat (SSE) ---
export function streamChat(
  kbId: number, query: string, conversationId: number | null,
  onMeta: (convId: number) => void,
  onToken: (t: string) => void,
  onDone: () => void,
  onError: (e: Error) => void,
): AbortController {
  const ctrl = new AbortController();
  fetch(`${BASE}/kb/${kbId}/chat`, {
    method: "POST", signal: ctrl.signal,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, conversation_id: conversationId }),
  }).then(async (resp) => {
    const reader = resp.body?.getReader(); if (!reader) return onDone();
    const dec = new TextDecoder(); let buf = "";
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split("\n"); buf = lines.pop() || "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const d = JSON.parse(line.slice(6));
          if (d.type === "done") return onDone();
          if (d.type === "meta" && d.conversation_id) onMeta(d.conversation_id);
          if (d.type === "token" && d.data) onToken(d.data);
        } catch { /* skip */ }
      }
    }
    onDone();
  }).catch((err) => { if (err.name !== "AbortError") onError(err); });
  return ctrl;
}
