from app.generation.base import ChatMessage
from app.retrieval.hybrid_search import SearchResult

SYSTEM_PROMPT = """You are CazzKB, a personal knowledge base assistant. Answer questions based on the provided context.

Guidelines:
- If the context contains relevant information, answer based on it and cite sources using [source] tags.
- If the context is insufficient, say so clearly and offer your best general knowledge.
- Use markdown formatting for clarity.
- Be concise and accurate. Don't make up information not present in the context.
- Do not use emojis. Use plain text and markdown formatting only.
- When citing, use the format: <cite source="filename" header="header_path">excerpt</cite>."""


def build_rag_messages(
    query: str,
    search_results: list[SearchResult],
    history: list[ChatMessage] | None = None,
) -> list[ChatMessage]:
    messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]

    if history:
        messages.extend(history[-6:])

    if search_results:
        context_parts = []
        for i, r in enumerate(search_results):
            source_id = f"source-{i + 1}"
            context_parts.append(
                f"[{source_id}] {r.source_file} > {r.header_path}\n{r.content}"
            )
        context = "\n\n---\n\n".join(context_parts)
        user_message = f"Context:\n\n{context}\n\nQuestion: {query}"
    else:
        user_message = f"Question: {query}\n\n(No relevant documents found in the knowledge base.)"

    messages.append(ChatMessage(role="user", content=user_message))
    return messages
