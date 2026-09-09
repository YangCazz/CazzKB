import json
import datetime
from pathlib import Path
from typing import Iterator

from app.config import AppConfig
from app.models.db import (
    KnowledgeBase, Document, Chunk, Conversation, Message, Artifact,
)
from app.ingestion.chunker import SemanticChunker, ChunkMetadata
from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.orchestrator import SearchOrchestrator
from app.generation.base import (
    ChatMessage, LLMProvider, get_llm_provider,
)
from app.generation.templates import build_rag_messages


class KBManager:
    def __init__(self, config: AppConfig, embed_provider: EmbeddingProvider):
        self.config = config
        self.embed_provider = embed_provider
        self.search = SearchOrchestrator(config, embed_provider)
        self._llm: LLMProvider | None = None

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider(
                factory=self.config.llm.factory,
                model=self.config.llm.model,
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url,
                max_tokens=self.config.llm.max_tokens,
                thinking_budget_tokens=self.config.llm.thinking_budget_tokens,
            )
        return self._llm

    # --- KB CRUD ---

    def create_kb(self, name: str, description: str = "") -> KnowledgeBase:
        return KnowledgeBase.create(name=name, description=description)

    def get_kb(self, kb_id: int) -> KnowledgeBase:
        return KnowledgeBase.get_by_id(kb_id)

    def list_kbs(self) -> list[KnowledgeBase]:
        return list(KnowledgeBase.select().order_by(KnowledgeBase.updated_at.desc()))

    def delete_kb(self, kb_id: int):
        kb = self.get_kb(kb_id)
        self.search.delete_kb(str(kb_id))
        kb.delete_instance(recursive=True)

    # --- Document Ingestion ---

    def ingest_document(self, kb_id: int, filename: str, content: bytes) -> Document:
        kb = self.get_kb(kb_id)

        upload_dir = Path(self.config.storage.upload_path) / str(kb_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        filepath = upload_dir / filename
        filepath.write_bytes(content)

        text = content.decode("utf-8")
        chunker = SemanticChunker(
            max_tokens=self.config.kb.chunk_size,
            overlap_tokens=self.config.kb.chunk_overlap,
        )
        chunks = chunker.chunk(text, filename)

        doc = Document.create(
            kb=kb,
            filename=filename,
            title=chunks[0].title if chunks else filename,
            source_date=chunks[0].date if chunks else "",
            categories=json.dumps(chunks[0].categories if chunks else []),
            tags=json.dumps(chunks[0].tags if chunks else []),
            chunk_count=len(chunks),
        )

        for i, chunk in enumerate(chunks):
            Chunk.create(
                document=doc,
                content=chunk.content,
                header_path=chunk.header_path,
                element_type=chunk.element_type,
                chunk_index=i,
                metadata_json=json.dumps({
                    "title": chunk.title,
                    "date": chunk.date,
                    "categories": chunk.categories,
                    "tags": chunk.tags,
                    "prev_chunk_id": chunk.prev_chunk_id,
                    "next_chunk_id": chunk.next_chunk_id,
                }),
            )

        self.search.index_chunks(str(kb_id), chunks)

        kb.chunk_count = kb.chunk_count + len(chunks)
        kb.updated_at = doc.ingested_at
        kb.save()

        return doc

    # --- Notebook-style sources ---

    def list_sources(self, kb_id: int) -> list[dict]:
        sources = (Document
                   .select()
                   .where(Document.kb_id == kb_id)
                   .order_by(Document.ingested_at.desc()))
        return [{
            "id": s.id,
            "filename": s.filename,
            "title": s.title or s.filename,
            "source_type": s.source_type,
            "summary": s.summary,
            "enabled": bool(s.enabled),
            "chunk_count": s.chunk_count,
            "source_date": s.source_date,
            "categories": json.loads(s.categories or "[]"),
            "tags": json.loads(s.tags or "[]"),
            "ingested_at": s.ingested_at.isoformat(),
        } for s in sources]

    def get_source(self, source_id: int) -> dict | None:
        try:
            source = Document.get_by_id(source_id)
            chunks = (Chunk
                      .select()
                      .where(Chunk.document_id == source_id)
                      .order_by(Chunk.chunk_index.asc()))
            return {
                "id": source.id,
                "kb_id": source.kb_id,
                "filename": source.filename,
                "title": source.title or source.filename,
                "source_type": source.source_type,
                "summary": source.summary,
                "enabled": bool(source.enabled),
                "source_date": source.source_date,
                "categories": json.loads(source.categories or "[]"),
                "tags": json.loads(source.tags or "[]"),
                "chunk_count": source.chunk_count,
                "ingested_at": source.ingested_at.isoformat(),
                "chunks": [{
                    "id": c.id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "header_path": c.header_path,
                    "element_type": c.element_type,
                    "metadata": json.loads(c.metadata_json or "{}"),
                } for c in chunks],
            }
        except Exception:
            return None

    def update_source(self, source_id: int, title: str | None = None,
                      summary: str | None = None, enabled: bool | None = None) -> dict | None:
        try:
            source = Document.get_by_id(source_id)
            if title is not None:
                source.title = title[:255]
            if summary is not None:
                source.summary = summary
            if enabled is not None:
                source.enabled = 1 if enabled else 0
            source.save()
            return self.get_source(source_id)
        except Exception:
            return None

    # --- Conversations ---

    def list_conversations(self, kb_id: int) -> list[dict]:
        convs = (Conversation
                 .select()
                 .where(Conversation.kb_id == kb_id)
                 .order_by(Conversation.created_at.desc()))
        return [{
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "message_count": Message.select().where(Message.conversation_id == c.id).count(),
        } for c in convs]

    def get_conversation(self, conv_id: int) -> dict | None:
        try:
            c = Conversation.get_by_id(conv_id)
            msgs = (Message
                    .select()
                    .where(Message.conversation_id == conv_id)
                    .order_by(Message.created_at.asc()))
            return {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "messages": [{"role": m.role, "content": m.content, "sources": m.sources_json, "created_at": m.created_at.isoformat()} for m in msgs],
            }
        except Exception:
            return None

    def delete_conversation(self, conv_id: int):
        try:
            c = Conversation.get_by_id(conv_id)
            c.delete_instance(recursive=True)
        except Exception:
            pass

    def rename_conversation(self, conv_id: int, title: str):
        try:
            c = Conversation.get_by_id(conv_id)
            c.title = title[:120]
            c.save()
        except Exception:
            pass

    # --- Notebook-style artifacts ---

    def list_artifacts(self, kb_id: int) -> list[dict]:
        artifacts = (Artifact
                     .select()
                     .where(Artifact.kb_id == kb_id)
                     .order_by(Artifact.updated_at.desc()))
        return [{
            "id": a.id,
            "title": a.title,
            "artifact_type": a.artifact_type,
            "content": a.content,
            "metadata": json.loads(a.metadata_json or "{}"),
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat(),
        } for a in artifacts]

    def create_artifact(self, kb_id: int, title: str, artifact_type: str,
                        content: str, metadata: dict | None = None) -> dict:
        kb = self.get_kb(kb_id)
        now = datetime.datetime.utcnow()
        artifact = Artifact.create(
            kb=kb,
            title=title[:255],
            artifact_type=artifact_type,
            content=content,
            metadata_json=json.dumps(metadata or {}),
            created_at=now,
            updated_at=now,
        )
        kb.updated_at = now
        kb.save()
        return {
            "id": artifact.id,
            "title": artifact.title,
            "artifact_type": artifact.artifact_type,
            "content": artifact.content,
            "metadata": json.loads(artifact.metadata_json or "{}"),
            "created_at": artifact.created_at.isoformat(),
            "updated_at": artifact.updated_at.isoformat(),
        }

    def get_artifact(self, artifact_id: int) -> dict | None:
        try:
            artifact = Artifact.get_by_id(artifact_id)
            return {
                "id": artifact.id,
                "kb_id": artifact.kb_id,
                "title": artifact.title,
                "artifact_type": artifact.artifact_type,
                "content": artifact.content,
                "metadata": json.loads(artifact.metadata_json or "{}"),
                "created_at": artifact.created_at.isoformat(),
                "updated_at": artifact.updated_at.isoformat(),
            }
        except Exception:
            return None

    def delete_artifact(self, artifact_id: int):
        try:
            artifact = Artifact.get_by_id(artifact_id)
            artifact.delete_instance()
        except Exception:
            pass

    # --- Chat ---

    def get_chunks(self, kb_id: int, offset: int = 0, limit: int = 50) -> list[dict]:
        chunks = (Chunk
                  .select()
                  .join(Document)
                  .where(Document.kb_id == kb_id)
                  .order_by(Chunk.id)
                  .offset(offset)
                  .limit(limit))
        return [{
            "id": c.id,
            "content": c.content[:200],
            "header_path": c.header_path,
            "element_type": c.element_type,
            "source_file": c.document.filename,
        } for c in chunks]

    def chat(self, kb_id: int, query: str,
             conversation_id: int | None = None) -> Iterator[str]:
        results = self.search.search(str(kb_id), query)

        history = []
        if conversation_id:
            msgs = (Message
                    .select()
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at.desc())
                    .limit(6))
            for m in reversed(list(msgs)):
                history.append(ChatMessage(role=m.role, content=m.content))

        messages = build_rag_messages(query, results, history)

        if conversation_id is None:
            conv = Conversation.create(kb=self.get_kb(kb_id), title=query[:80])
            conversation_id = conv.id

        Message.create(
            conversation_id=conversation_id,
            role="user",
            content=query,
        )

        yield json.dumps({"type": "meta", "conversation_id": conversation_id})

        full_response = ""
        for event in self.llm.chat_stream(messages):
            if event.type == "thinking":
                yield json.dumps({"type": "thinking", "data": event.data})
            else:
                full_response += event.data
                yield json.dumps({"type": "token", "data": event.data})

        source_ids = [r.chunk_id for r in results]
        Message.create(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            sources_json=json.dumps(source_ids),
        )
