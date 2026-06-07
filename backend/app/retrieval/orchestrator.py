from pathlib import Path

import chromadb

from app.config import AppConfig
from app.retrieval.embeddings import EmbeddingProvider
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid_search import reciprocal_rank_fusion, SearchResult
from app.retrieval.reranker import RerankerProvider, RerankDoc, get_reranker
from app.ingestion.chunker import ChunkMetadata


class SearchOrchestrator:
    def __init__(self, config: AppConfig, embed_provider: EmbeddingProvider):
        self.config = config
        self.embed_provider = embed_provider
        self.bm25 = BM25Index()

        chroma_path = Path(config.storage.chroma_path)
        chroma_path.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(chroma_path))

        self._reranker: RerankerProvider | None = None

    @property
    def reranker(self) -> RerankerProvider:
        if self._reranker is None:
            self._reranker = get_reranker(
                factory=self.config.reranker.factory,
                model=self.config.reranker.model,
            )
        return self._reranker

    def get_or_create_collection(self, kb_id: str) -> chromadb.Collection:
        name = f"kb_{kb_id}"
        try:
            return self.chroma_client.get_collection(name)
        except Exception:
            return self.chroma_client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )

    def index_chunks(self, kb_id: str, chunks: list[ChunkMetadata]):
        collection = self.get_or_create_collection(kb_id)
        texts = [c.content for c in chunks]
        ids = [f"{c.source_file}:{c.chunk_index}" for c in chunks]
        embeddings = self.embed_provider.embed(texts)
        metadatas = [{
            "source_file": c.source_file,
            "title": c.title,
            "header_path": c.header_path,
            "element_type": c.element_type,
        } for c in chunks]
        collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        for chunk_id, text in zip(ids, texts):
            self.bm25.add(chunk_id, text)
        self.bm25.build()

    def search(self, kb_id: str, query: str, top_k: int | None = None) -> list[SearchResult]:
        if top_k is None:
            top_k = self.config.kb.top_k

        collection = self.get_or_create_collection(kb_id)
        query_embedding = self.embed_provider.embed([query])[0]
        dense_raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,
            include=["documents", "metadatas", "distances"],
        )

        dense_results = []
        if dense_raw["ids"] and dense_raw["ids"][0]:
            for i, chunk_id in enumerate(dense_raw["ids"][0]):
                similarity = 1.0 - dense_raw["distances"][0][i]
                dense_results.append((
                    chunk_id,
                    dense_raw["documents"][0][i],
                    similarity,
                ))

        sparse_raw = self.bm25.search(query, top_k=top_k * 2)
        sparse_results = [(r.chunk_id, r.text, r.score) for r in sparse_raw]

        # RRF fusion: get more candidates for reranker to refine
        multiplier = self.config.retrieval.candidate_multiplier
        candidates = reciprocal_rank_fusion(
            dense_results, sparse_results,
            k=self.config.retrieval.rrf_k,
            dense_weight=self.config.retrieval.dense_weight,
            top_k=top_k * multiplier,
        )

        # Reranker: score and trim to top_k
        if len(candidates) > 1:
            docs = [RerankDoc(content=c.content, title=c.title) for c in candidates]
            reranked = self.reranker.rerank(query, docs, top_k=top_k)
            # Map reranker results back to SearchResult objects
            ranked_ids = [doc.content[:80] for doc, _score in reranked]
            content_map = {c.content[:80]: c for c in candidates}
            results = []
            for doc, score in reranked:
                key = doc.content[:80]
                if key in content_map:
                    sr = content_map[key]
                    sr.score = score
                    results.append(sr)
        else:
            results = candidates

        # Enrich with metadata
        dense_meta_map = {}
        if dense_raw["metadatas"] and dense_raw["metadatas"][0]:
            for i, chunk_id in enumerate(dense_raw["ids"][0]):
                dense_meta_map[chunk_id] = dense_raw["metadatas"][0][i]

        for r in results:
            meta = dense_meta_map.get(r.chunk_id, {})
            r.source_file = meta.get("source_file", "")
            r.title = meta.get("title", "")
            r.header_path = meta.get("header_path", "")
            r.element_type = meta.get("element_type", "")

        return results

    def delete_kb(self, kb_id: str):
        try:
            self.chroma_client.delete_collection(f"kb_{kb_id}")
        except Exception:
            pass
