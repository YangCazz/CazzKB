export interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  chunk_count: number;
  created_at: string;
}

export interface Document {
  id: number;
  filename: string;
  title: string;
  chunk_count: number;
}

export interface Chunk {
  id: number;
  content: string;
  header_path: string;
  element_type: string;
  source_file: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface SearchSource {
  chunk_id: string;
  source_file: string;
  header_path: string;
  excerpt: string;
}
