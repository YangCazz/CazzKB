from app.ingestion.chunker import SemanticChunker


SAMPLE = """---
title: "Gated Attention"
date: 2025-12-01
categories: ["Deep Learning"]
tags: ["Mamba", "Attention"]
---

# Selective State Spaces

## The Problem

Standard SSMs lack input-dependent selectivity. This means every token
gets processed through the same fixed A, B, C matrices regardless of
its content.

In Mamba, the B and C matrices become functions of the input x_t.

## The Solution

Mamba introduces a selective scan algorithm that materializes the
hidden state only for the output, achieving linear-time sequence
modeling while maintaining input-dependent processing.
"""


def test_chunker_extracts_frontmatter_metadata():
    chunker = SemanticChunker(max_tokens=200)
    chunks = chunker.chunk(SAMPLE, "mamba.md")
    assert len(chunks) > 0
    assert chunks[0].title == "Gated Attention"
    assert chunks[0].date == "2025-12-01"
    assert "Deep Learning" in chunks[0].categories
    assert "Mamba" in chunks[0].tags


def test_chunker_preserves_header_path():
    chunker = SemanticChunker(max_tokens=200)
    chunks = chunker.chunk(SAMPLE, "mamba.md")
    header_chunks = [c for c in chunks if c.element_type == "header"]
    assert len(header_chunks) >= 1
    paths = [c.header_path for c in chunks if c.header_path]
    assert any("/Selective State Spaces" in p for p in paths)


def test_chunker_links_neighbors():
    chunker = SemanticChunker(max_tokens=100)
    chunks = chunker.chunk(SAMPLE, "mamba.md")
    if len(chunks) >= 2:
        assert chunks[0].next_chunk_id == "mamba.md:1"
        assert chunks[1].prev_chunk_id == "mamba.md:0"


def test_chunker_content_present():
    chunker = SemanticChunker(max_tokens=200)
    chunks = chunker.chunk(SAMPLE, "mamba.md")
    full_text = " ".join(c.content for c in chunks)
    assert "selective scan" in full_text.lower()
