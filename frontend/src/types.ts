export interface KnowledgeBase {
  id: number; name: string; description: string;
  chunk_count: number; created_at: string;
}

export interface Conversation {
  id: number; title: string; created_at: string; message_count: number;
}

export interface Message {
  role: "user" | "assistant"; content: string;
  responseTime?: number; sources?: string; created_at?: string;
}
