from collections.abc import Iterator

from app.generation.base import (
    ChatMessage, ChatResponse, LLMProvider, StreamEvent, register_llm,
)


@register_llm
class AnthropicProvider(LLMProvider):
    _FACTORY_NAME = "anthropic"

    def __init__(self, model: str, api_key: str, base_url: str = "", max_tokens: int = 4096,
                 thinking_budget_tokens: int = 0):
        import anthropic
        self.model = model
        self.max_tokens = max_tokens
        self.thinking_budget_tokens = thinking_budget_tokens
        client_args = {"auth_token": api_key}
        if base_url:
            client_args["base_url"] = base_url
        self.client = anthropic.Anthropic(**client_args)

    def chat(self, messages: list[ChatMessage], stream: bool = False) -> ChatResponse:
        system, msgs = self._convert_messages(messages)
        kwargs = {"model": self.model, "max_tokens": self.max_tokens, "messages": msgs}
        if system:
            kwargs["system"] = system
        if self.thinking_budget_tokens > 0:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.thinking_budget_tokens}
        if stream:
            text = ""
            with self.client.messages.stream(**kwargs) as s:
                for event in s:
                    if event.type == "content_block_delta":
                        try:
                            text += event.delta.text
                        except AttributeError:
                            pass
            return ChatResponse(content=text)
        else:
            resp = self.client.messages.create(**kwargs)
            content = ""
            for block in resp.content:
                if block.type == "text":
                    content += block.text
            return ChatResponse(content=content)

    def chat_stream(self, messages: list[ChatMessage]) -> Iterator[StreamEvent]:
        system, msgs = self._convert_messages(messages)
        kwargs = {"model": self.model, "max_tokens": self.max_tokens, "messages": msgs}
        if system:
            kwargs["system"] = system
        if self.thinking_budget_tokens > 0:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.thinking_budget_tokens}
        with self.client.messages.stream(**kwargs) as s:
            for event in s:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "thinking") and event.delta.thinking:
                        yield StreamEvent(type="thinking", data=event.delta.thinking)
                    elif hasattr(event.delta, "text") and event.delta.text:
                        yield StreamEvent(type="text", data=event.delta.text)

    def _convert_messages(self, messages: list[ChatMessage]) -> tuple[str, list[dict]]:
        system = ""
        result = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                result.append({"role": m.role, "content": m.content})
        return system, result


@register_llm
class DeepSeekProvider(LLMProvider):
    _FACTORY_NAME = "deepseek"

    def __init__(self, model: str, api_key: str, base_url: str = "https://api.deepseek.com",
                 max_tokens: int = 4096, thinking_budget_tokens: int = 0):
        import openai
        self.model = model
        self.max_tokens = max_tokens
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, messages: list[ChatMessage], stream: bool = False) -> ChatResponse:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        if stream:
            text = ""
            resp = self.client.chat.completions.create(
                model=self.model, messages=msgs, max_tokens=self.max_tokens, stream=True,
            )
            for chunk in resp:
                if chunk.choices[0].delta.content:
                    text += chunk.choices[0].delta.content
            return ChatResponse(content=text)
        else:
            resp = self.client.chat.completions.create(
                model=self.model, messages=msgs, max_tokens=self.max_tokens,
            )
            return ChatResponse(content=resp.choices[0].message.content)

    def chat_stream(self, messages: list[ChatMessage]) -> Iterator[StreamEvent]:
        msgs = [{"role": m.role, "content": m.content} for m in messages]
        resp = self.client.chat.completions.create(
            model=self.model, messages=msgs, max_tokens=self.max_tokens, stream=True,
        )
        for chunk in resp:
            if chunk.choices[0].delta.content:
                yield StreamEvent(type="text", data=chunk.choices[0].delta.content)
