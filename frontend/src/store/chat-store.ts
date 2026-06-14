import { create } from "zustand";
import type { KnowledgeBase, Conversation, Message } from "../types";
import * as api from "../api/client";

interface ChatState {
  // KB
  kbs: KnowledgeBase[];
  selectedKbId: number | null;
  loadKBs: () => Promise<void>;
  selectKB: (id: number) => void;
  createKB: (name: string) => Promise<void>;
  deleteKB: (id: number) => Promise<void>;
  uploadDoc: (file: File) => Promise<void>;
  // Conversations
  conversations: Conversation[];
  activeConvId: number | null;
  loadConversations: () => Promise<void>;
  selectConversation: (id: number) => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
  renameConversation: (id: number, title: string) => Promise<void>;
  // Messages
  messages: Message[];
  isStreaming: boolean;
  abortRef: { current: AbortController | null };
  sendMessage: (query: string) => void;
  editMessage: (index: number, content: string) => void;
  clearChat: () => void;
}

export const useStore = create<ChatState>((set, get) => ({
  kbs: [],
  selectedKbId: null,
  conversations: [],
  activeConvId: null,
  messages: [],
  isStreaming: false,
  abortRef: { current: null },

  loadKBs: async () => {
    try {
      const kbs = await api.listKBs();
      const currentId = get().selectedKbId;
      if (kbs.length === 1 && currentId === null) {
        set({ kbs, selectedKbId: kbs[0].id });
        get().loadConversations();
      } else {
        set({ kbs });
      }
    } catch { /* */ }
  },

  selectKB: (id: number) => {
    set({ selectedKbId: id, activeConvId: null, messages: [], conversations: [] });
    get().loadConversations();
  },

  createKB: async (name: string) => {
    const kb = await api.createKB(name);
    set((s) => ({ kbs: [...s.kbs, kb] }));
  },

  deleteKB: async (id: number) => {
    await api.deleteKB(id);
    set((s) => ({
      kbs: s.kbs.filter((k) => k.id !== id),
      selectedKbId: s.selectedKbId === id ? null : s.selectedKbId,
      activeConvId: s.selectedKbId === id ? null : s.activeConvId,
      messages: s.selectedKbId === id ? [] : s.messages,
    }));
  },

  uploadDoc: async (file: File) => {
    const kbId = get().selectedKbId;
    if (!kbId) return;
    await api.uploadDocument(kbId, file);
    get().loadKBs();
  },

  loadConversations: async () => {
    const kbId = get().selectedKbId;
    if (!kbId) { set({ conversations: [] }); return; }
    try { set({ conversations: await api.listConversations(kbId) }); } catch { /* */ }
  },

  selectConversation: async (id: number) => {
    try {
      const conv = await api.getConversation(id);
      const msgs: Message[] = conv.messages.map((m) => ({
        role: m.role as "user" | "assistant", content: m.content,
        sources: m.sources, created_at: m.created_at,
      }));
      set({ activeConvId: id, messages: msgs });
    } catch { /* */ }
  },

  deleteConversation: async (id: number) => {
    await api.deleteConversation(id);
    set((s) => ({
      conversations: s.conversations.filter((c) => c.id !== id),
      activeConvId: s.activeConvId === id ? null : s.activeConvId,
      messages: s.activeConvId === id ? [] : s.messages,
    }));
  },

  renameConversation: async (id: number, title: string) => {
    await api.renameConversation(id, title);
    get().loadConversations();
  },

  clearChat: () => {
    get().abortRef.current?.abort();
    set({ messages: [], activeConvId: null, isStreaming: false });
  },

  editMessage: (index: number, content: string) => {
    const { selectedKbId, activeConvId, abortRef } = get();
    if (!selectedKbId || !content.trim()) return;

    abortRef.current?.abort();

    // Update the user message at index and truncate everything after it
    const msgs = get().messages.slice(0, index + 1);
    msgs[index] = { ...msgs[index], content };

    // Start a new assistant response
    const assistantMsg: Message = { role: "assistant", content: "" };
    set({ messages: [...msgs, assistantMsg], isStreaming: true });

    const startTime = Date.now();
    let firstTokenRecorded = false;
    let streamContent = "";
    const ctrl = api.streamChat(
      selectedKbId, content, activeConvId,
      (convId) => set({ activeConvId: convId }),
      (token) => {
        streamContent += token;
        set((s) => {
          const updatedMsgs = [...s.messages];
          const updatedMsg: Message = { ...updatedMsgs[updatedMsgs.length - 1], content: streamContent };
          if (!firstTokenRecorded) {
            firstTokenRecorded = true;
            updatedMsg.firstTokenTime = Math.round((Date.now() - startTime) / 100) / 10;
          }
          updatedMsgs[updatedMsgs.length - 1] = updatedMsg;
          return { messages: updatedMsgs };
        });
      },
      (thinking) => {
        set((s) => {
          const updatedMsgs = [...s.messages];
          const prevThinking = updatedMsgs[updatedMsgs.length - 1].thinking || "";
          updatedMsgs[updatedMsgs.length - 1] = { ...updatedMsgs[updatedMsgs.length - 1], thinking: prevThinking + thinking };
          return { messages: updatedMsgs };
        });
      },
      () => {
        const elapsed = Math.round((Date.now() - startTime) / 100) / 10;
        set((s) => {
          const finalMsgs = [...s.messages];
          finalMsgs[finalMsgs.length - 1] = { ...finalMsgs[finalMsgs.length - 1], responseTime: elapsed };
          return { messages: finalMsgs, isStreaming: false };
        });
        get().loadConversations();
      },
      (err) => { console.error("Chat error:", err); set({ isStreaming: false }); },
    );
    set({ abortRef: { current: ctrl } });
  },

  sendMessage: (query: string) => {
    const { selectedKbId, activeConvId, abortRef } = get();
    if (!selectedKbId || !query.trim()) return;

    const userMsg: Message = { role: "user", content: query };
    const assistantMsg: Message = { role: "assistant", content: "" };
    set((s) => ({ messages: [...s.messages, userMsg, assistantMsg], isStreaming: true }));

    const startTime = Date.now();
    let firstTokenRecorded = false;
    let content = "";

    abortRef.current?.abort();
    const ctrl = api.streamChat(
      selectedKbId, query, activeConvId,
      (convId) => set({ activeConvId: convId }),
      (token) => {
        content += token;
        set((s) => {
          const msgs = [...s.messages];
          const updatedMsg: Message = { ...msgs[msgs.length - 1], content };
          if (!firstTokenRecorded) {
            firstTokenRecorded = true;
            updatedMsg.firstTokenTime = Math.round((Date.now() - startTime) / 100) / 10;
          }
          msgs[msgs.length - 1] = updatedMsg;
          return { messages: msgs };
        });
      },
      (thinking) => {
        set((s) => {
          const msgs = [...s.messages];
          const prevThinking = msgs[msgs.length - 1].thinking || "";
          msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], thinking: prevThinking + thinking };
          return { messages: msgs };
        });
      },
      () => {
        const elapsed = Math.round((Date.now() - startTime) / 100) / 10;
        set((s) => {
          const msgs = [...s.messages];
          msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], responseTime: elapsed };
          return { messages: msgs, isStreaming: false };
        });
        // Refresh conversation list after new message
        get().loadConversations();
      },
      (err) => { console.error("Chat error:", err); set({ isStreaming: false }); },
    );
    set({ abortRef: { current: ctrl } });
  },
}));
