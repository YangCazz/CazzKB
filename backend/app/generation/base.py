from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    content: str
    usage: dict | None = None


class LLMProvider(ABC):
    _FACTORY_NAME: str = ""

    @abstractmethod
    def chat(self, messages: list[ChatMessage], stream: bool = False) -> ChatResponse:
        """Send a chat completion request."""

    @abstractmethod
    def chat_stream(self, messages: list[ChatMessage]) -> Iterator[str]:
        """Stream chat completion, yielding content delta strings."""


_registry: dict[str, type[LLMProvider]] = {}


def register_llm(cls: type[LLMProvider]) -> type[LLMProvider]:
    if cls._FACTORY_NAME:
        _registry[cls._FACTORY_NAME] = cls
    return cls


def get_llm_provider(factory: str, model: str, api_key: str,
                     base_url: str = "", max_tokens: int = 4096) -> LLMProvider:
    cls = _registry.get(factory)
    if cls is None:
        raise ValueError(f"Unknown LLM factory: {factory}. Available: {list(_registry.keys())}")
    return cls(model=model, api_key=api_key, base_url=base_url, max_tokens=max_tokens)
