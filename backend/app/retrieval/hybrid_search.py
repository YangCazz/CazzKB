from dataclasses import dataclass


@dataclass
class SearchResult:
    chunk_id: str
    content: str
    score: float
    dense_score: float = 0.0
    sparse_score: float = 0.0
    source_file: str = ""
    title: str = ""
    header_path: str = ""
    element_type: str = ""


def reciprocal_rank_fusion(
    dense_results: list[tuple[str, str, float]],
    sparse_results: list[tuple[str, str, float]],
    k: int = 60,
    dense_weight: float = 0.7,
    top_k: int = 8,
) -> list[SearchResult]:
    dense_rank: dict[str, int] = {}
    sparse_rank: dict[str, int] = {}

    for rank, (chunk_id, _, _) in enumerate(dense_results, start=1):
        dense_rank[chunk_id] = rank
    for rank, (chunk_id, _, _) in enumerate(sparse_results, start=1):
        sparse_rank[chunk_id] = rank

    all_ids = set(dense_rank.keys()) | set(sparse_rank.keys())

    content_map: dict[str, str] = {}
    dense_scores: dict[str, float] = {}
    sparse_scores: dict[str, float] = {}

    for chunk_id, content, score in dense_results:
        content_map[chunk_id] = content
        dense_scores[chunk_id] = score
    for chunk_id, content, score in sparse_results:
        if chunk_id not in content_map:
            content_map[chunk_id] = content
        sparse_scores[chunk_id] = score

    fused = []
    for chunk_id in all_ids:
        d_rank = dense_rank.get(chunk_id, len(dense_results) + 1)
        s_rank = sparse_rank.get(chunk_id, len(sparse_results) + 1)
        rrf = dense_weight * (1.0 / (k + d_rank)) + (1 - dense_weight) * (1.0 / (k + s_rank))
        fused.append((chunk_id, rrf))

    fused.sort(key=lambda x: x[1], reverse=True)

    results = []
    for chunk_id, rrf_score in fused[:top_k]:
        results.append(SearchResult(
            chunk_id=chunk_id,
            content=content_map.get(chunk_id, ""),
            score=rrf_score,
            dense_score=dense_scores.get(chunk_id, 0),
            sparse_score=sparse_scores.get(chunk_id, 0),
        ))
    return results
