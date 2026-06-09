from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Registry-based embedding provider. Subclasses set _FACTORY_NAME."""
    _FACTORY_NAME: str = ""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Output dimension of this embedding model."""


_registry: dict[str, type[EmbeddingProvider]] = {}


def register_embedding(cls: type[EmbeddingProvider]) -> type[EmbeddingProvider]:
    if cls._FACTORY_NAME:
        _registry[cls._FACTORY_NAME] = cls
    return cls


def get_embedding_provider(factory: str, model: str, api_key: str,
                           base_url: str = "", **kwargs) -> EmbeddingProvider:
    cls = _registry.get(factory)
    if cls is None:
        raise ValueError(f"Unknown embedding factory: {factory}. "
                         f"Available: {list(_registry.keys())}")
    return cls(model=model, api_key=api_key, base_url=base_url, **kwargs)


@register_embedding
class OpenAIEmbedding(EmbeddingProvider):
    _FACTORY_NAME = "openai"

    def __init__(self, model: str, api_key: str, base_url: str = "", **kwargs):
        import openai
        self.model = model
        client_args = {"api_key": api_key}
        if base_url:
            client_args["base_url"] = base_url
        self.client = openai.OpenAI(**client_args)

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]

    @property
    def dimension(self) -> int:
        return 1536


_OLLAMA_EMBED_DIMS: dict[str, int] = {
    "bge-m3": 1024,
    "bge-large": 1024,
    "nomic-embed-text": 768,
    "mxbai-embed-large": 1024,
    "all-minilm": 384,
}


@register_embedding
class OllamaEmbedding(EmbeddingProvider):
    _FACTORY_NAME = "ollama"

    def __init__(self, model: str, api_key: str = "", base_url: str = "",
                 dimension: int = 0):
        self.model = model
        self.base_url = base_url or "http://localhost:11434"
        self._dimension = dimension or _OLLAMA_EMBED_DIMS.get(model, 1024)

    def embed(self, texts: list[str]) -> list[list[float]]:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import requests, time

        def _embed_one(text: str) -> list[float]:
            last_err = None
            for attempt in range(3):
                try:
                    resp = requests.post(f"{self.base_url}/api/embeddings", json={
                        "model": self.model, "prompt": text,
                    }, timeout=30)
                    resp.raise_for_status()
                    return resp.json()["embedding"]
                except Exception as e:
                    last_err = e
                    time.sleep(1 + attempt)
            raise last_err

        results = [None] * len(texts)
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = {executor.submit(_embed_one, t): i for i, t in enumerate(texts)}
            for f in as_completed(futures):
                idx = futures[f]
                results[idx] = f.result()

        if not self._dimension and results[0]:
            self._dimension = len(results[0])
        return results

    @property
    def dimension(self) -> int:
        return self._dimension
