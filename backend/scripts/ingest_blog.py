"""Ingest YangCazz.github.io blog posts into CazzKB.

Usage:
    cd backend
    E:/miniconda/envs/CazzKB/python.exe scripts/ingest_blog.py
"""

import os
import sys
from pathlib import Path

# Ensure backend is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.models.db import init_db
from app.config import load_config
from app.retrieval.embeddings import get_embedding_provider
from app.kb_manager.manager import KBManager

BLOG_POSTS_DIR = Path("D:/Projects/YangCazz.github.io/_posts")
KB_NAME = "YangCazz Blog"
SUPPORTED_EXTS = {".md", ".markdown"}


def collect_posts(root: Path) -> list[Path]:
    posts = []
    for f in sorted(root.iterdir()):
        if f.suffix in SUPPORTED_EXTS:
            posts.append(f)
    return posts


def main():
    if not BLOG_POSTS_DIR.exists():
        print(f"Blog directory not found: {BLOG_POSTS_DIR}")
        sys.exit(1)

    posts = collect_posts(BLOG_POSTS_DIR)
    print(f"Found {len(posts)} posts in {BLOG_POSTS_DIR}")

    # Change to backend dir so all paths (data/, config/) resolve correctly
    backend_dir = Path(__file__).resolve().parent.parent
    os.chdir(str(backend_dir))

    # Init
    init_db()
    config = load_config()
    embed_provider = get_embedding_provider(
        factory=config.embedding.factory,
        model=config.embedding.model,
        api_key=config.embedding.api_key,
        base_url=config.embedding.base_url,
    )
    manager = KBManager(config, embed_provider)

    # Create or reuse KB
    existing = manager.list_kbs()
    kb = None
    for e in existing:
        if e.name == KB_NAME:
            kb = e
            print(f"Using existing KB: id={kb.id}, chunks={kb.chunk_count}")
            break

    if kb is None:
        kb = manager.create_kb(name=KB_NAME, description="YangCazz technical blog")
        print(f"Created KB: id={kb.id}")

    # Ingest - index_chunks no longer rebuilds BM25, we build once at the end
    success = 0
    failed = 0

    for i, post in enumerate(posts):
        try:
            content = post.read_bytes()
            doc = manager.ingest_document(kb.id, post.name, content)
            print(f"[{i+1}/{len(posts)}] OK  {post.name}  ({doc.chunk_count} chunks)", flush=True)
            success += 1
        except Exception as e:
            print(f"[{i+1}/{len(posts)}] ERR {post.name}: {e}", flush=True)
            failed += 1

    # Build BM25 once after all chunks indexed
    print("Building BM25 index...", flush=True)
    manager.search.build_bm25()
    print("BM25 ready.", flush=True)

    kb = manager.get_kb(kb.id)
    print(f"\nDone. {success} ingested, {failed} failed.")
    print(f"KB '{kb.name}': {kb.chunk_count} total chunks.")


if __name__ == "__main__":
    main()
