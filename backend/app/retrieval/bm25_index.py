import re
from dataclasses import dataclass
from rank_bm25 import BM25Okapi

# Stop words for Chinese-English technical blog retrieval.
# BM25's IDF already down-weights high-frequency terms, but explicit filtering
# prevents these from polluting sparse vector space and improves fusion quality.
_STOP_WORDS: set[str] = {
    # English function words
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "will", "would", "shall", "should", "may", "might", "must", "can", "could",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "its", "they", "them", "their",
    "this", "that", "these", "those", "here", "there",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either", "neither",
    "if", "then", "else", "when", "where", "why", "how", "all", "each", "every",
    "which", "who", "whom", "what", "very", "just", "than", "too", "also",
    # Frequently occurring in technical docs, low signal
    "fig", "figure", "et", "al", "e.g", "i.e", "paper", "using", "based", "show", "shown",
    "one", "two", "first", "second", "can", "used", "use", "well",
    # Chinese function characters (single-char particles)
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
    "都", "一", "上", "也", "很", "到", "说", "要", "去", "你",
    "会", "着", "看", "好", "自己", "这", "那", "他", "她", "们",
    "没", "被", "把", "让", "对", "从", "向", "与", "而", "及",
    "或", "但", "所", "为", "以", "之", "其", "可", "能", "只",
    "中", "大", "小", "更", "最", "多", "少", "新", "旧", "高",
    "低", "长", "短", "前", "后", "左", "右", "内", "外", "个",
    "里", "已", "将", "正", "再", "又", "还", "才", "便", "则",
    "此", "该", "各", "等", "些", "每", "某", "哪", "怎", "么",
    "吗", "吧", "呢", "啊", "哦", "嗯", "哈",
}


def _tokenize(text: str) -> list[str]:
    cleaned = text.lower().replace(".", " ").replace(",", " ").replace("!", " ") \
        .replace("?", " ").replace(":", " ").replace(";", " ").replace("(", " ") \
        .replace(")", " ").replace("[", " ").replace("]", " ").replace("{", " ") \
        .replace("}", " ")
    tokens = cleaned.split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


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
