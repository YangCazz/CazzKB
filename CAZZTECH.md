# CazzKB · Role in CazzTech

## Identity

**Knowledge storage & retrieval layer** for CazzTech. Provides semantic search, hybrid retrieval (dense + sparse + rerank), and multi-model chat over private documents.

## Dependencies On

- Ollama (local embeddings, optional)
- LLM APIs (DeepSeek/Anthropic)

## Consumed By

- CazzAi (knowledge retrieval integration)
- CazzPatentSkill (reference document retrieval)
- All CazzTech agents (as memory backend)

## Development Plan

| Phase | Goal | Status |
|-------|------|:------:|
| Core | Semantic chunking + hybrid retrieval + multi-LLM | ✅ |
| Integration | Connect as shared knowledge layer for all projects | ○ |
| Advanced | Agent-driven knowledge graph construction | ○ |

## Key Interfaces

- REST API on port 8000 (FastAPI)
- React UI on port 5173
- SSE streaming for LLM responses
```
