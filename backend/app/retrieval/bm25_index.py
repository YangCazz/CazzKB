from dataclasses import dataclass
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return text.lower().replace(".", " ").replace(",", " ").replace("!", " ") \
        .replace("?", " ").replace(":", " ").replace(";", " ").split()


@dataclass
class BM25Result:
    chunk_id: str
    score: float
    text: str


class BM25Index:
    def __init__(self):
        self._chunks: list[dict] = []
        self._bm25: BM25Okapi | None = None

    def add(self, chunk_id: str, text: str):
        self._chunks.append({"id": chunk_id, "text": text})

    def build(self):
        tokenized = [_tokenize(c["text"]) for c in self._chunks]
        self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 8) -> list[BM25Result]:
        if self._bm25 is None:
            return []
        tokenized_query = _tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in indexed[:top_k]:
            if score > 0:
                results.append(BM25Result(
                    chunk_id=self._chunks[idx]["id"],
                    score=float(score),
                    text=self._chunks[idx]["text"],
                ))
        return results

    @property
    def doc_count(self) -> int:
        return len(self._chunks)
