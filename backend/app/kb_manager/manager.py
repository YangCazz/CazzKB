import json
from pathlib import Path
from typing import Iterator

from app.config import AppConfig
from app.models.db import (
    KnowledgeBase, Document, Chunk, Conversation, Message,
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
        kb.save()

        return doc

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

        full_response = ""
        for token in self.llm.chat_stream(messages):
            full_response += token
            yield token

        source_ids = [r.chunk_id for r in results]
        Message.create(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            sources_json=json.dumps(source_ids),
        )
