from app.retrieval.embeddings import get_embedding_provider, _registry


def test_registry_contains_openai():
    assert "openai" in _registry
    assert "ollama" in _registry


def test_get_provider_unknown_raises():
    try:
        get_embedding_provider("nonexistent", "m", "k")
        assert False, "should have raised"
    except ValueError as e:
        assert "nonexistent" in str(e)
