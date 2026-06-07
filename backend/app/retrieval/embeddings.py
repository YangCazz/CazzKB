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
                           base_url: str = "") -> EmbeddingProvider:
    cls = _registry.get(factory)
    if cls is None:
        raise ValueError(f"Unknown embedding factory: {factory}. "
                         f"Available: {list(_registry.keys())}")
    return cls(model=model, api_key=api_key, base_url=base_url)


@register_embedding
class OpenAIEmbedding(EmbeddingProvider):
    _FACTORY_NAME = "openai"

    def __init__(self, model: str, api_key: str, base_url: str = ""):
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


@register_embedding
class OllamaEmbedding(EmbeddingProvider):
    _FACTORY_NAME = "ollama"

    def __init__(self, model: str, api_key: str = "", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def embed(self, texts: list[str]) -> list[list[float]]:
        import requests
        embeddings = []
        for text in texts:
            resp = requests.post(f"{self.base_url}/api/embeddings", json={
                "model": self.model, "prompt": text,
            })
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])
        return embeddings

    @property
    def dimension(self) -> int:
        return 768  # default for nomic-embed-text
