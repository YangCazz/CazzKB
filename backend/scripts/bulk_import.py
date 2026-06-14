"""Bulk import markdown files into CazzKB from YangCazz.github.io blog."""
import sys
from pathlib import Path
import requests

API_BASE = "http://localhost:8000/api"
SOURCE_DIR = Path("D:/YangCazz/YangCazz.github.io")

SKIP_DIRS = {"_posts_backup", "_site", ".git", "node_modules", "assets", "_includes",
             "_layouts", "_sass", "_scripts", "template"}


def main():
    # Create KB
    resp = requests.post(f"{API_BASE}/kb", json={"name": "My Knowledge", "description": "YangCazz blog posts and docs"})
    if resp.status_code != 200:
        print(f"Failed to create KB: {resp.text}")
        sys.exit(1)
    kb = resp.json()
    kb_id = kb["id"]
    print(f"Created KB: {kb['name']} (id={kb_id})")

    # Collect all markdown files
    md_files = []
    for f in SOURCE_DIR.rglob("*.md"):
        # Skip excluded dirs
        parts = set(f.relative_to(SOURCE_DIR).parts)
        if parts & SKIP_DIRS:
            continue
        md_files.append(f)

    md_files.sort()
    print(f"Found {len(md_files)} markdown files to import\n")

    success = 0
    for i, fpath in enumerate(md_files):
        rel = fpath.relative_to(SOURCE_DIR)
        try:
            content = fpath.read_bytes()
            resp = requests.post(
                f"{API_BASE}/kb/{kb_id}/upload",
                files={"file": (fpath.name, content, "text/markdown")},
            )
            if resp.status_code == 200:
                doc = resp.json()
                print(f"[{i+1}/{len(md_files)}] OK  {rel}  ({doc['chunk_count']} chunks)")
                success += 1
            else:
                print(f"[{i+1}/{len(md_files)}] ERR {rel}  ({resp.status_code}: {resp.text[:100]})")
        except Exception as e:
            print(f"[{i+1}/{len(md_files)}] EXC {rel}  ({e})")

    print(f"\nDone. Imported {success}/{len(md_files)} files.")


if __name__ == "__main__":
    main()
