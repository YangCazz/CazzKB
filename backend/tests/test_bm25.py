from app.retrieval.bm25_index import BM25Index


def test_bm25_add_and_search():
    idx = BM25Index()
    idx.add("c0", "Mamba is a selective state space model")
    idx.add("c1", "Transformers use self-attention mechanisms")
    idx.add("c2", "State space models are used in control theory")
    idx.build()
    results = idx.search("selective state space", top_k=2)
    assert len(results) >= 1
    assert results[0].chunk_id == "c0"
    assert results[0].score > 0


def test_bm25_empty_search_before_build():
    idx = BM25Index()
    idx.add("c0", "hello world")
    results = idx.search("hello", top_k=3)
    assert results == []
