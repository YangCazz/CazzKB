import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class KBConfig:
    name: str = "Default"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 8
    similarity_threshold: float = 0.65


@dataclass
class EmbeddingConfig:
    factory: str = "openai"
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    api_key: str = ""
    base_url: str = ""


@dataclass
class LLMConfig:
    factory: str = "anthropic"
    model: str = "claude-sonnet-4-6"
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 4096


@dataclass
class RerankerConfig:
    factory: str = "none"
    model: str = ""


@dataclass
class RetrievalConfig:
    rrf_k: int = 60
    dense_weight: float = 0.7
    candidate_multiplier: int = 3


@dataclass
class StorageConfig:
    chroma_path: str = "data/chroma"
    db_path: str = "data/cazzkb.db"
    upload_path: str = "data/uploads"


@dataclass
class AppConfig:
    kb: KBConfig = field(default_factory=KBConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    reranker: RerankerConfig = field(default_factory=RerankerConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


_VAR_RE = re.compile(r"\$\{(\w+)\}")


def _resolve_env(value: str) -> str:
    """Replace ${VAR} with os.environ[VAR]."""
    if not isinstance(value, str):
        return value
    def _replacer(m):
        return os.environ.get(m.group(1), "")
    return _VAR_RE.sub(_replacer, value)


def _apply_env(obj):
    """Recursively resolve env vars in a dataclass."""
    for field_name in obj.__dataclass_fields__:
        val = getattr(obj, field_name)
        if isinstance(val, str):
            setattr(obj, field_name, _resolve_env(val))
        elif hasattr(val, "__dataclass_fields__"):
            _apply_env(val)


def load_config(path: str | None = None) -> AppConfig:
    if path is None:
        path = os.environ.get("CAZZKB_CONFIG", "config/default.yaml")
    config = AppConfig()
    if Path(path).exists():
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
        _merge_config(config, raw)
    _apply_env(config)
    return config


def _merge_config(config: AppConfig, raw: dict):
    if "kb" in raw:
        for k, v in raw["kb"].items():
            if hasattr(config.kb, k):
                setattr(config.kb, k, v)
    if "embedding" in raw:
        for k, v in raw["embedding"].items():
            if hasattr(config.embedding, k):
                setattr(config.embedding, k, v)
    if "llm" in raw:
        for k, v in raw["llm"].items():
            if hasattr(config.llm, k):
                setattr(config.llm, k, v)
    if "retrieval" in raw:
        for k, v in raw["retrieval"].items():
            if hasattr(config.retrieval, k):
                setattr(config.retrieval, k, v)
    if "reranker" in raw:
        for k, v in raw["reranker"].items():
            if hasattr(config.reranker, k):
                setattr(config.reranker, k, v)
    if "storage" in raw:
        for k, v in raw["storage"].items():
            if hasattr(config.storage, k):
                setattr(config.storage, k, v)
