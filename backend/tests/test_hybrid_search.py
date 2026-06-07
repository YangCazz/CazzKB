from app.retrieval.hybrid_search import reciprocal_rank_fusion


def test_rrf_fuses_rankings():
    dense = [
        ("c0", "Mamba is a state space model", 0.95),
        ("c1", "Transformers use attention", 0.80),
        ("c2", "RNNs process sequentially", 0.60),
    ]
    sparse = [
        ("c2", "RNNs process sequentially", 5.2),
        ("c0", "Mamba is a state space model", 3.8),
        ("c3", "LSTMs have gates", 2.1),
    ]
    results = reciprocal_rank_fusion(dense, sparse, k=60, top_k=4)
    assert len(results) <= 4
    top_ids = [r.chunk_id for r in results[:2]]
    assert "c0" in top_ids


def test_rrf_handles_empty_sparse():
    dense = [("c0", "content", 0.9)]
    results = reciprocal_rank_fusion(dense, [], k=60, top_k=3)
    assert len(results) == 1
    assert results[0].chunk_id == "c0"
