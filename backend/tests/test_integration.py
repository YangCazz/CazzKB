import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Allow the OpenAI client to be constructed without a real API key.
# The embed method is mocked below, so this key is never used for an actual API call.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy-key")


@pytest.fixture(autouse=True)
def _setup_db():
    """Use a temporary file database instead of :memory:.

    TestClient runs handlers in worker threads, which breaks peewee's
    in-memory SQLite (:memory: creates a per-connection database).
    Using a temp file avoids this issue entirely.
    """
    from app.models.db import db, init_db

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db.init(db_path)
    init_db()
    yield
    db.close()
    for sfx in ("", "-wal", "-shm"):
        p = db_path + sfx
        if os.path.exists(p):
            try:
                os.unlink(p)
            except PermissionError:
                pass


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _dummy_embed(self, texts: list[str]) -> list[list[float]]:
    """Return dummy embeddings so the test does not need a real API key."""
    return [[0.0] * 1536 for _ in texts]


def test_full_flow(client):
    # 1. Create KB
    resp = client.post("/api/kb", json={"name": "Integration Test"})
    assert resp.status_code == 200
    kb_id = resp.json()["id"]

    # 2. Upload document
    md_content = """---
title: "Test Document"
date: 2026-06-07
categories: ["AI"]
---

# Getting Started

This is a test document about RAG systems.

## Architecture

A typical RAG system has three components:
- Retriever
- Generator
- Knowledge base
"""
    with patch("app.retrieval.embeddings.OpenAIEmbedding.embed", _dummy_embed):
        resp = client.post(f"/api/kb/{kb_id}/upload",
                           files={"file": ("doc.md", md_content.encode(), "text/markdown")})
    assert resp.status_code == 200
    assert resp.json()["chunk_count"] > 0

    # 3. List chunks
    resp = client.get(f"/api/kb/{kb_id}/chunks")
    assert resp.status_code == 200
    chunks = resp.json()
    assert len(chunks) > 0

    # 4. Get KB stats
    resp = client.get(f"/api/kb/{kb_id}")
    assert resp.json()["chunk_count"] > 0

    # 5. Delete KB
    resp = client.delete(f"/api/kb/{kb_id}")
    assert resp.status_code == 200
