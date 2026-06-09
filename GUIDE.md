<div align="right">
  <a href="GUIDE.zh-CN.md">中文</a>
</div>

# CazzKB Guide

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Local Deployment](#local-deployment)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Roadmap](#roadmap)

---

## Prerequisites

| Dependency | Purpose | Install |
|------------|---------|---------|
| Python 3.11+ | Backend | `conda create -n cazzkb python=3.11` |
| Node.js 18+ | Frontend | `winget install OpenJS.NodeJS` |
| Ollama | Local Embedding | `ollama pull bge-m3` |

---

## Installation

### 1. Clone

```bash
git clone https://github.com/YangCazz/CazzKB.git
cd CazzKB
```

### 2. Backend

```bash
cd backend
conda create -n cazzkb python=3.11 -y
conda activate cazzkb
uv pip install -r requirements.txt
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Configure

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your API key:

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. Launch

```bash
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Open `http://localhost:5173`.

---

## Configuration

Edit `backend/config/default.yaml`:

### LLM

```yaml
llm:
  factory: "anthropic"                      # DeepSeek via Anthropic-compatible endpoint
  model: "deepseek-v4-pro[1m]"
  api_key: "${DEEPSEEK_API_KEY}"            # Injected from .env
  base_url: "https://api.deepseek.com/anthropic"
  max_tokens: 4096
```

Available factories: `anthropic`, `deepseek`

### Embedding

```yaml
embedding:
  factory: "ollama"
  model: "bge-m3"
  dimension: 1024
```

Available factories: `ollama`, `openai`

### Retrieval

```yaml
retrieval:
  rrf_k: 60
  dense_weight: 0.7
  candidate_multiplier: 3

reranker:
  factory: "none"         # none | bge | llm
  model: "BAAI/bge-reranker-v2-m3"
```

### Storage

```yaml
storage:
  chroma_path: "data/chroma"
  db_path: "data/cazzkb.db"
  upload_path: "data/uploads"
```

All paths are local — zero cloud dependencies.

---

## Local Deployment

Fully offline setup with no cloud APIs:

| Component | Solution | Config |
|-----------|----------|--------|
| LLM | Ollama + qwen2.5 / deepseek-r1 | Add `OllamaProvider` (PR welcome) |
| Embedding | Ollama + bge-m3 | `embedding.factory: ollama` |
| Reranker | FlagEmbedding + bge-reranker-v2-m3 | `pip install FlagEmbedding` + `reranker.factory: bge` |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/kb` | Create knowledge base |
| `GET` | `/api/kb` | List knowledge bases |
| `GET` | `/api/kb/{id}` | Get KB details |
| `DELETE` | `/api/kb/{id}` | Delete KB |
| `POST` | `/api/kb/{id}/upload` | Upload Markdown |
| `GET` | `/api/kb/{id}/chunks` | List chunks |
| `POST` | `/api/kb/{id}/chat` | Chat (SSE) |
| `GET` | `/api/kb/{id}/conversations` | List conversations |
| `GET` | `/api/conversations/{id}` | Get conversation |
| `PATCH` | `/api/conversations/{id}` | Rename conversation |
| `DELETE` | `/api/conversations/{id}` | Delete conversation |

### SSE Event Format

```
data: {"type":"meta","conversation_id":42}
data: {"type":"token","data":"Mamba"}
data: {"type":"token","data":" is a"}
...
data: {"type":"done"}
```

---

## Project Structure

```
CazzKB/
├── backend/
│   ├── app/
│   │   ├── api/              FastAPI routes + SSE
│   │   ├── ingestion/        Markdown parser + chunker
│   │   ├── retrieval/        Embedding + BM25 + RRF + Reranker
│   │   ├── generation/       LLM providers + RAG prompts
│   │   ├── kb_manager/       Central orchestrator
│   │   └── models/           Peewee ORM (SQLite)
│   ├── config/default.yaml
│   ├── scripts/              Data import
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── chat/         MessageTimeline · FloatingComposer
│       │   ├── sidebar/      SidebarFrame · TreeRow · SearchField
│       │   └── shared/       CopyButton · DevBadge · MarkdownComponents
│       ├── store/            Zustand 5
│       └── api/              REST + SSE client
├── images/                   Architecture & pipeline diagrams
├── GUIDE.md                  This file
├── LICENSE
└── README.md
```

---

## Contributing

Issues and PRs are welcome.

```bash
# Dev setup
cd backend && uv pip install -e ".[dev]"
cd frontend && npm install

# Run tests
cd backend && python -m pytest tests/ -v --rootdir=.
```

Please follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix a bug
docs: update documentation
chore: maintenance work
test: add or update tests
```

---

## Roadmap

| Phase | Status | Content |
|-------|--------|---------|
| **1. RAG** | ✓ Done | Semantic chunking + hybrid retrieval + reranker + multi-provider + Web UI |
| **2. Graph** | Planned | Knowledge graph · entity-relation query |
| **3. Agentic** | Planned | Autonomous multi-turn retrieval · tool calling |
| **4. Memory** | Planned | Cross-session memory · retrieval-free fallback |
