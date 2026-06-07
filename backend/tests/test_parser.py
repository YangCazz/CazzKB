from app.ingestion.parser import parse_markdown, ElementType


SAMPLE_MD = """---
title: "Test Post"
date: 2026-06-07
categories: ["testing"]
---

# Introduction

This is a test paragraph.

## Code Example

```python
def hello():
    return "world"
```

## Data Table

| Name | Value |
|------|-------|
| Foo  | 1     |
| Bar  | 2     |

### Sub Section

- Item one
- Item two

> A blockquote here.

Final paragraph.
"""


def test_parse_extracts_frontmatter():
    elements = parse_markdown(SAMPLE_MD)
    fm = elements[0]
    assert fm.type == ElementType.FRONTMATTER
    assert 'title: "Test Post"' in fm.content


def test_parse_extracts_headers():
    elements = parse_markdown(SAMPLE_MD)
    headers = [e for e in elements if e.type == ElementType.HEADER]
    assert len(headers) == 4
    assert headers[0].content == "Introduction"
    assert headers[0].level == 1
    assert headers[0].header_path == "/Introduction"
    assert headers[3].content == "Sub Section"
    assert headers[3].header_path == "/Introduction/Data Table/Sub Section"


def test_parse_protects_code_block():
    elements = parse_markdown(SAMPLE_MD)
    codes = [e for e in elements if e.type == ElementType.CODE]
    assert len(codes) == 1
    assert 'def hello():' in codes[0].content


def test_parse_extracts_table():
    elements = parse_markdown(SAMPLE_MD)
    tables = [e for e in elements if e.type == ElementType.TABLE]
    assert len(tables) == 1
    assert "| Name | Value |" in tables[0].content


def test_parse_extracts_list_and_quote():
    elements = parse_markdown(SAMPLE_MD)
    lists = [e for e in elements if e.type == ElementType.LIST]
    quotes = [e for e in elements if e.type == ElementType.BLOCKQUOTE]
    assert len(lists) >= 1
    assert len(quotes) == 1
    assert "A blockquote here" in quotes[0].content
