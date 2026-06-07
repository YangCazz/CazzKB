from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


@dataclass
class RerankDoc:
    content: str
    title: str = ""


class RerankerProvider(ABC):
    _FACTORY_NAME: str = ""

    @abstractmethod
    def rerank(self, query: str, docs: list[RerankDoc],
               top_k: int | None = None) -> list[tuple[RerankDoc, float]]:
        """Score documents against query. Returns sorted (doc, score) descending."""


_registry: dict[str, type[RerankerProvider]] = {}


def register_reranker(cls: type[RerankerProvider]) -> type[RerankerProvider]:
    if cls._FACTORY_NAME:
        _registry[cls._FACTORY_NAME] = cls
    return cls


def get_reranker(factory: str, model: str = "", **kwargs) -> RerankerProvider:
    cls = _registry.get(factory)
    if cls is None:
        raise ValueError(f"Unknown reranker factory: {factory}. "
                         f"Available: {list(_registry.keys())}")
    return cls(model=model, **kwargs)


@register_reranker
class NoopReranker(RerankerProvider):
    """Pass-through: returns documents in original order with score 1.0."""
    _FACTORY_NAME = "none"

    def __init__(self, model: str = "", **kwargs):
        pass

    def rerank(self, query: str, docs: list[RerankDoc],
               top_k: int | None = None) -> list[tuple[RerankDoc, float]]:
        results = [(doc, 1.0) for doc in docs]
        if top_k is not None:
            results = results[:top_k]
        return results


@register_reranker
class BGEReranker(RerankerProvider):
    """Local Cross-Encoder reranker using FlagEmbedding."""
    _FACTORY_NAME = "bge"

    def __init__(self, model: str = "BAAI/bge-reranker-v2-m3", **kwargs):
        from FlagEmbedding import FlagReranker
        self._model = FlagReranker(model, use_fp16=True)

    def rerank(self, query: str, docs: list[RerankDoc],
               top_k: int | None = None) -> list[tuple[RerankDoc, float]]:
        pairs = [[query, doc.content] for doc in docs]
        scores = self._model.compute_score(pairs, normalize=True)

        # compute_score returns single float if one pair, list if multiple
        if not isinstance(scores, list):
            scores = [scores]

        scored = list(zip(docs, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        if top_k is not None:
            scored = scored[:top_k]
        return scored


@register_reranker
class LLMReranker(RerankerProvider):
    """Use any registered LLM provider to score relevance per document."""
    _FACTORY_NAME = "llm"

    def __init__(self, model: str = "", llm=None, **kwargs):
        self._llm = llm

    def rerank(self, query: str, docs: list[RerankDoc],
               top_k: int | None = None) -> list[tuple[RerankDoc, float]]:
        if self._llm is None:
            raise RuntimeError("LLMReranker requires an LLM provider instance. "
                               "Pass `llm=` to get_reranker().")

        scored = []
        for doc in docs:
            score = self._score_one(query, doc)
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        if top_k is not None:
            scored = scored[:top_k]
        return scored

    def _score_one(self, query: str, doc: RerankDoc) -> float:
        from app.generation.base import ChatMessage
        prompt = (
            "Score how relevant this document is to the query. "
            "Output ONLY a number between 0 and 1 (e.g. 0.87).\n\n"
            f"Query: {query}\n\n"
            f"Document: {doc.content[:1500]}"
        )
        msgs = [ChatMessage(role="user", content=prompt)]
        resp = self._llm.chat(msgs)
        try:
            return float(resp.content.strip()[:10])
        except ValueError:
            return 0.5
