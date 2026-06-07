from dataclasses import dataclass, field

from app.ingestion.parser import Element, ElementType, parse_markdown


@dataclass
class ChunkMetadata:
    content: str
    source_file: str
    title: str = ""
    header_path: str = ""
    element_type: str = "text"
    date: str = ""
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    chunk_index: int = 0
    prev_chunk_id: str = ""
    next_chunk_id: str = ""


def _estimate_tokens(text: str) -> int:
    """Simple token estimator: ~4 chars = 1 token for English, ~2 chars for Chinese."""
    chars = len(text)
    cjk = sum(1 for c in text if "一" <= c <= "鿿" or "぀" <= c <= "ゟ")
    return max(1, (chars - cjk) // 4 + cjk // 2)


class SemanticChunker:
    def __init__(self, max_tokens: int = 512, overlap_tokens: int = 50):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self, markdown_text: str, source_file: str,
              frontmatter: dict | None = None) -> list[ChunkMetadata]:
        elements = parse_markdown(markdown_text)
        if frontmatter is None:
            frontmatter = self._extract_frontmatter(elements)
        merged = self._merge_elements(elements)
        chunks = self._split_oversized(merged, source_file, frontmatter)
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
            if i > 0:
                chunk.prev_chunk_id = f"{source_file}:{i - 1}"
            if i < len(chunks) - 1:
                chunk.next_chunk_id = f"{source_file}:{i + 1}"
        return chunks

    def _extract_frontmatter(self, elements: list[Element]) -> dict:
        for elem in elements:
            if elem.type == ElementType.FRONTMATTER:
                try:
                    import frontmatter as fm_lib
                    import io
                    post = fm_lib.load(io.StringIO("---\n" + elem.content + "\n---\n"))
                    return dict(post.metadata)
                except Exception:
                    return {}
        return {}

    def _merge_elements(self, elements: list[Element]) -> list[tuple[str, ElementType, str, dict]]:
        merged: list[tuple[str, ElementType, str, dict]] = []
        buffer = ""
        buf_type = ElementType.TEXT
        buf_header = ""
        buf_meta = {}

        protected_types = {ElementType.CODE, ElementType.TABLE, ElementType.MATH,
                          ElementType.MERMAID, ElementType.FRONTMATTER}

        def flush():
            nonlocal buffer, buf_type, buf_header, buf_meta
            if buffer.strip():
                merged.append((buffer.strip(), buf_type, buf_header, buf_meta))
            buffer = ""
            buf_type = ElementType.TEXT
            buf_header = ""
            buf_meta = {}

        for elem in elements:
            if elem.type == ElementType.FRONTMATTER:
                continue
            if elem.type == ElementType.HEADER:
                flush()
                merged.append((elem.content, elem.type, elem.header_path, elem.meta))
                continue
            if elem.type in protected_types:
                flush()
                merged.append((elem.content, elem.type, elem.header_path, elem.meta))
                continue
            if _estimate_tokens(buffer) + _estimate_tokens(elem.content) > self.max_tokens:
                flush()
            if not buffer:
                buf_type = elem.type
                buf_header = elem.header_path
            separator = "\n\n" if buffer else ""
            buffer += separator + elem.content
            buf_meta = {**buf_meta, **elem.meta}
        flush()
        return merged

    def _split_oversized(self, merged: list[tuple[str, ElementType, str, dict]],
                         source_file: str, frontmatter: dict) -> list[ChunkMetadata]:
        chunks: list[ChunkMetadata] = []
        title = frontmatter.get("title", source_file)
        date = str(frontmatter.get("date", ""))
        categories = frontmatter.get("categories", [])
        tags = frontmatter.get("tags", [])
        if isinstance(categories, str):
            categories = [c.strip() for c in categories.strip("[]").split(",") if c.strip()]
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
        for content, etype, header_path, meta in merged:
            if _estimate_tokens(content) <= self.max_tokens:
                chunks.append(ChunkMetadata(
                    content=content, source_file=source_file,
                    title=title, header_path=header_path,
                    element_type=etype.value,
                    date=date, categories=categories, tags=tags,
                ))
            else:
                sub_chunks = self._split_long_text(content, etype, header_path)
                for sc in sub_chunks:
                    chunks.append(ChunkMetadata(
                        content=sc, source_file=source_file,
                        title=title, header_path=header_path,
                        element_type=etype.value,
                        date=date, categories=categories, tags=tags,
                    ))
        return chunks

    def _split_long_text(self, text: str, etype: ElementType,
                         header_path: str) -> list[str]:
        paragraphs = text.split("\n\n")
        chunks = []
        buf = ""
        for para in paragraphs:
            if _estimate_tokens(buf + para) > self.max_tokens and buf:
                chunks.append(buf.strip())
                words = buf.split()
                overlap_size = max(1, self.overlap_tokens // 4)
                overlap_words = words[-overlap_size:]
                buf = " ".join(overlap_words) + "\n\n" + para
            else:
                buf = (buf + "\n\n" + para).strip()
        if buf.strip():
            chunks.append(buf.strip())
        return chunks
