import os
import tempfile

# Use a dummy key so the OpenAI client can be constructed
# without needing a real API key for tests that don't call the API.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy-key")

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(autouse=True)
def _setup_db():
    """Override conftest's in-memory fixture with a temporary file database.

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


def test_create_and_list_kb(client):
    resp = client.post("/api/kb", json={"name": "Test KB", "description": "desc"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test KB"

    resp = client.get("/api/kb")
    assert resp.status_code == 200
    kbs = resp.json()
    assert len(kbs) >= 1


def test_get_kb_404(client):
    resp = client.get("/api/kb/99999")
    assert resp.status_code == 404


@pytest.mark.xfail(reason="Needs real OPENAI_API_KEY for embeddings", strict=False)
def test_upload_document(client):
    resp = client.post("/api/kb", json={"name": "Upload Test"})
    kb_id = resp.json()["id"]

    md_content = b"# Test\n\nHello world."
    resp = client.post(f"/api/kb/{kb_id}/upload",
                       files={"file": ("test.md", md_content, "text/markdown")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.md"
    assert data["chunk_count"] > 0


@pytest.mark.xfail(reason="Needs real OPENAI_API_KEY for embeddings", strict=False)
def test_chat_stream(client):
    resp = client.post("/api/kb", json={"name": "Chat Test"})
    kb_id = resp.json()["id"]

    resp = client.post(f"/api/kb/{kb_id}/chat", json={"query": "test query"})
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
