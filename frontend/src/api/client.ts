import type { KnowledgeBase, Document, Chunk } from "../types";

const BASE = "/api";

export async function createKB(name: string, description = ""): Promise<KnowledgeBase> {
  const resp = await fetch(`${BASE}/kb`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
  return resp.json();
}

export async function listKBs(): Promise<KnowledgeBase[]> {
  const resp = await fetch(`${BASE}/kb`);
  return resp.json();
}

export async function getKB(id: number): Promise<KnowledgeBase> {
  const resp = await fetch(`${BASE}/kb/${id}`);
  if (!resp.ok) throw new Error("KB not found");
  return resp.json();
}

export async function deleteKB(id: number): Promise<void> {
  await fetch(`${BASE}/kb/${id}`, { method: "DELETE" });
}

export async function uploadDocument(kbId: number, file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${BASE}/kb/${kbId}/upload`, { method: "POST", body: form });
  return resp.json();
}

export async function listChunks(kbId: number): Promise<Chunk[]> {
  const resp = await fetch(`${BASE}/kb/${kbId}/chunks`);
  return resp.json();
}

export function streamChat(
  kbId: number,
  query: string,
  conversationId: number | null,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): AbortController {
  const controller = new AbortController();
  fetch(`${BASE}/kb/${kbId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, conversation_id: conversationId }),
    signal: controller.signal,
  })
    .then(async (resp) => {
      const reader = resp.body?.getReader();
      if (!reader) return onDone();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6));
            if (data.done) return onDone();
            if (data.token) onToken(data.token);
          }
        }
      }
      onDone();
    })
    .catch((err) => {
      if (err.name !== "AbortError") onError(err);
    });
  return controller;
}
