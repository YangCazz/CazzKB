export interface KnowledgeBase {
  id: number; name: string; description: string;
  chunk_count: number; created_at: string;
}

export type Notebook = KnowledgeBase;

export interface UploadedDocument {
  id: number;
  filename: string;
  title: string;
  chunk_count: number;
}

export interface Source {
  id: number;
  filename: string;
  title: string;
  source_type: string;
  summary: string;
  enabled: boolean;
  chunk_count: number;
  source_date: string;
  categories: string[];
  tags: string[];
  ingested_at: string;
}

export interface SourceChunk {
  id: number;
  chunk_index: number;
  content: string;
  header_path: string;
  element_type: string;
  metadata: Record<string, unknown>;
}

export interface SourceDetail extends Source {
  kb_id: number;
  chunks: SourceChunk[];
}

export interface Artifact {
  id: number;
  kb_id?: number;
  title: string;
  artifact_type: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: number; title: string; created_at: string; message_count: number;
}

export interface Message {
  role: "user" | "assistant"; content: string; thinking?: string;
  responseTime?: number; firstTokenTime?: number; sources?: string; created_at?: string;
}
